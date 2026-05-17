import bcrypt
import jwt
from flask import request, jsonify, current_app
from src.config.db import Database
import os
from datetime import datetime, timedelta

def generar_token(persona_id, usuario_id, rol, primer_login, es_token_cambio=False):
    """Genera JWT con expiración"""
    if es_token_cambio:
        # Token especial para cambio de contraseña (15 minutos)
        expiracion = datetime.utcnow() + timedelta(minutes=15)
        payload = {
            'persona_id': persona_id,
            'es_token_cambio': True,
            'exp': expiracion
        }
    else:
        # Token normal (8 horas)
        expiracion = datetime.utcnow() + timedelta(hours=8)
        payload = {
            'persona_id': persona_id,
            'usuario_id': usuario_id,
            'rol': rol,
            'primer_login': primer_login,
            'exp': expiracion
        }
    
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')

def hash_password(password):
    """Genera un hash bcrypt de la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def login():
    """Autenticación de usuario"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email y contraseña requeridos"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    # Buscar persona por email junto con su usuario
    sql = """
        SELECT p.id as persona_id, p.rol, p.primer_login, p.activo,
               u.id as usuario_id, u.password_hash
        FROM personas p
        JOIN usuarios u ON p.id = u.persona_id
        WHERE p.email = %s
    """
    
    result = Database.execute_query(sql, (email,), fetch_one=True)
    
    if not result:
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Verificar si el empleado está activo
    if not result['activo']:
        return jsonify({"error": "Usuario dado de baja"}), 403
    
    # Verificar contraseña con bcrypt
    password_bytes = password.encode('utf-8')
    hash_bytes = result['password_hash'].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, hash_bytes):
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Actualizar último login
    update_sql = "UPDATE usuarios SET ultimo_login = NOW() WHERE id = %s"
    Database.execute_query(update_sql, (result['usuario_id'],))
    
    # Decidir tipo de token según primer_login
    if result['primer_login']:
        # Primer login: token especial para cambiar contraseña
        token = generar_token(
            result['persona_id'], 
            None, 
            None, 
            True,
            es_token_cambio=True
        )
        return jsonify({
            "token": token,
            "requires_change": True,
            "message": "Debe cambiar su contraseña"
        }), 200
    else:
        # Login normal
        token = generar_token(
            result['persona_id'],
            result['usuario_id'],
            result['rol'],
            False
        )
        return jsonify({
            "token": token,
            "requires_change": False,
            "rol": result['rol'],
            "message": "Login exitoso"
        }), 200

def cambiar_password():
    """Cambiar contraseña (requiere token especial de cambio)"""
    data = request.get_json()
    
    if not data or not data.get('nueva_password'):
        return jsonify({"error": "Nueva contraseña requerida"}), 400
    
    nueva_password = data.get('nueva_password')
    persona_id = request.persona_id  # Viene del middleware token_cambio_requerido
    
    # Validar longitud mínima
    if len(nueva_password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    # Hashear nueva contraseña
    password_hash = bcrypt.hashpw(
        nueva_password.encode('utf-8'), 
        bcrypt.gensalt(10)
    ).decode('utf-8')
    
    # Actualizar contraseña y desactivar primer_login
    sql_usuarios = "UPDATE usuarios SET password_hash = %s WHERE persona_id = %s"
    sql_personas = "UPDATE personas SET primer_login = 0 WHERE id = %s"
    
    Database.execute_query(sql_usuarios, (password_hash, persona_id))
    Database.execute_query(sql_personas, (persona_id,))
    
    # Generar token normal para uso posterior
    # Primero obtener datos actualizados
    sql_datos = """
        SELECT p.rol, u.id as usuario_id
        FROM personas p
        JOIN usuarios u ON p.id = u.persona_id
        WHERE p.id = %s
    """
    datos = Database.execute_query(sql_datos, (persona_id,), fetch_one=True)
    
    token_normal = generar_token(
        persona_id,
        datos['usuario_id'],
        datos['rol'],
        False
    )
    
    return jsonify({
        "message": "Contraseña actualizada correctamente",
        "token": token_normal
    }), 200