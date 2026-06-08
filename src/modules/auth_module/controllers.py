import bcrypt
import jwt
from flask import request, jsonify
from src.core.database import Database
import os
from datetime import datetime, timedelta

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
    
    result = Database.execute_query(sql, (email,), fetch_one=True)
    
    if not result:
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    if not result['activo']:
        return jsonify({"error": "Usuario dado de baja"}), 403
    
    if not bcrypt.checkpw(password.encode('utf-8'), result['password_hash'].encode('utf-8')):
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Actualizar último login
    update_sql = "UPDATE usuarios SET ultimo_login = CURRENT_TIMESTAMP WHERE id = ?"
    Database.execute_query(update_sql, (result['usuario_id'],))
    
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

def cambiar_password():
    # Esta función requiere el middleware token_cambio_requerido
    # La implementaremos después con el middleware correspondiente
    pass