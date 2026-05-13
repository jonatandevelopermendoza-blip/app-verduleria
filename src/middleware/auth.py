import jwt
from functools import wraps
from flask import request, jsonify, current_app
import os

def token_requerido(f):
    """Decorador para proteger rutas que requieren token JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en el header Authorization
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "Token requerido"}), 401
        
        try:
            # Decodificar token
            payload = jwt.decode(
                token, 
                os.getenv('JWT_SECRET_KEY'), 
                algorithms=['HS256']
            )
            # Guardar información del usuario en request
            request.usuario_id = payload.get('usuario_id')
            request.persona_id = payload.get('persona_id')
            request.rol = payload.get('rol')
            request.primer_login = payload.get('primer_login')
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    return decorated

def token_cambio_requerido(f):
    """Decorador para rutas que requieren token especial de cambio de contraseña"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({"error": "Token requerido"}), 401
        
        try:
            payload = jwt.decode(
                token, 
                os.getenv('JWT_SECRET_KEY'), 
                algorithms=['HS256']
            )
            # Verificar que sea un token de cambio (no el normal)
            if not payload.get('es_token_cambio'):
                return jsonify({"error": "Se requiere token especial de cambio de contraseña"}), 403
            
            request.persona_id = payload.get('persona_id')
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    return decorated

def rol_requerido(roles_permitidos):
    """Decorador para verificar roles (usar después de token_requerido)"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'rol'):
                return jsonify({"error": "No autenticado"}), 401
            
            if request.rol not in roles_permitidos:
                return jsonify({"error": "Permisos insuficientes"}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator