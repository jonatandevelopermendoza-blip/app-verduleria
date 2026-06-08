import bcrypt
import jwt
from flask import request, jsonify
from src.core.database import Database
import os
from datetime import datetime, timedelta
from src.utils.logger import log_action, log_error

def hash_password(password):
    """Genera un hash bcrypt de la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def generar_token(persona_id, usuario_id, rol, primer_login, es_token_cambio=False):
    """Genera JWT con expiración"""
    if es_token_cambio:
        expiracion = datetime.utcnow() + timedelta(minutes=15)
        payload = {
            'persona_id': persona_id,
            'es_token_cambio': True,
            'exp': expiracion
        }
    else:
        expiracion = datetime.utcnow() + timedelta(hours=8)
        payload = {
            'persona_id': persona_id,
            'usuario_id': usuario_id,
            'rol': rol,
            'primer_login': primer_login,
            'exp': expiracion
        }
    
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY', 'secret-key'), algorithm='HS256')

def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        log_action('LOGIN_FALLIDO', details="Faltan credenciales", level='warning')
        return jsonify({"error": "Email y contraseña requeridos"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    sql = """
        SELECT p.id as persona_id, p.rol, p.primer_login, p.activo,
               u.id as usuario_id, u.password_hash
        FROM personas p
        JOIN usuarios u ON p.id = u.persona_id
        WHERE p.email = ?
    """
    
    try:
        result = Database.execute_query(sql, (email,), fetch_one=True)
        
        if not result:
            log_action('LOGIN_FALLIDO', user_email=email, details="Usuario no existe", level='warning')
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        if not result['activo']:
            log_action('LOGIN_DENEGADO', user_email=email, user_id=result['persona_id'], 
                      details="Usuario dado de baja", level='warning')
            return jsonify({"error": "Usuario dado de baja"}), 403
        
        if not bcrypt.checkpw(password.encode('utf-8'), result['password_hash'].encode('utf-8')):
            log_action('LOGIN_FALLIDO', user_email=email, user_id=result['persona_id'], 
                      details="Contraseña incorrecta", level='warning')
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        # Actualizar último login
        update_sql = "UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?"
        Database.execute_query(update_sql, (result['usuario_id'],))
        
        log_action('LOGIN_EXITOSO', user_id=result['persona_id'], user_email=email, 
                  details=f"Rol: {result['rol']}")
        
        if result['primer_login']:
            token = generar_token(result['persona_id'], None, None, True, es_token_cambio=True)
            return jsonify({
                "token": token,
                "requires_change": True,
                "message": "Debe cambiar su contraseña"
            }), 200
        else:
            token = generar_token(result['persona_id'], result['usuario_id'], result['rol'], False)
            return jsonify({
                "token": token,
                "requires_change": False,
                "rol": result['rol'],
                "message": "Login exitoso"
            }), 200
            
    except Exception as e:
        log_error("Error en login", user_email=email, exception=e)
        return jsonify({"error": "Error interno del servidor"}), 500
    
def cambiar_password():
    """POST /auth/cambiar-password - Cambiar contraseña (requiere token especial)"""
    from flask import request, jsonify
    from src.middleware.auth import token_cambio_requerido
    from src.core.database import Database
    import bcrypt
    
    data = request.get_json()
    
    if not data or not data.get('nueva_password'):
        return jsonify({"error": "Nueva contraseña requerida"}), 400
    
    nueva_password = data.get('nueva_password')
    
    # Obtener persona_id del token (debe venir del middleware)
    # Por ahora, lo tomamos del token manualmente
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token requerido"}), 401
    
    token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
    if not token:
        return jsonify({"error": "Token inválido"}), 401
    
    # Decodificar token para obtener persona_id
    import jwt
    import os
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET_KEY', 'secret-key'), algorithms=['HS256'])
        persona_id = payload.get('persona_id')
        
        # Verificar que sea token de cambio
        if not payload.get('es_token_cambio'):
            return jsonify({"error": "Se requiere token especial de cambio de contraseña"}), 403
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401
    
    # Validar longitud mínima
    if len(nueva_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    # Hashear nueva contraseña
    password_hash = bcrypt.hashpw(
        nueva_password.encode('utf-8'), 
        bcrypt.gensalt(10)
    ).decode('utf-8')
    
    # Actualizar contraseña y desactivar primer_login
    sql_usuarios = "UPDATE usuarios SET password_hash = ? WHERE persona_id = ?"
    sql_personas = "UPDATE personas SET primer_login = 0 WHERE id = ?"
    
    Database.execute_query(sql_usuarios, (password_hash, persona_id))
    Database.execute_query(sql_personas, (persona_id,))
    
    # Generar token normal para uso posterior
    sql_datos = """
        SELECT p.rol, u.id as usuario_id
        FROM personas p
        JOIN usuarios u ON p.id = u.persona_id
        WHERE p.id = ?
    """
    datos = Database.execute_query(sql_datos, (persona_id,), fetch_one=True)
    
    token_normal = generar_token(persona_id, datos['usuario_id'], datos['rol'], False)
    
    from src.utils.logger import log_action
    log_action('CAMBIO_CONTRASENA', user_id=persona_id, level='info')
    
    return jsonify({
        "message": "Contraseña actualizada correctamente",
        "token": token_normal,
        "rol": datos['rol']
    }), 200