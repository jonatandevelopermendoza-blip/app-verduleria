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
            from src.utils.logger import log_action
            log_action('ACCESO_DENEGADO', details=f"IP: {request.remote_addr}, Sin token", level='warning')
            return jsonify({"error": "Token requerido"}), 401
        
        try:
            payload = jwt.decode(
                token, 
                os.getenv('JWT_SECRET_KEY', 'secret-key'), 
                algorithms=['HS256']
            )
            
            # Guardar información del usuario en request
            request.persona_id = payload.get('persona_id')
            request.usuario_id = payload.get('usuario_id')
            request.rol = payload.get('rol')
            request.primer_login = payload.get('primer_login')
            request.token_es_cambio = payload.get('es_token_cambio', False)
            
            # Log de acceso a ruta protegida (solo para debug)
            # from src.utils.logger import log_action
            # log_action('ACCESO_API', user_id=request.persona_id, details=f"Endpoint: {request.path}")
            
        except jwt.ExpiredSignatureError:
            from src.utils.logger import log_action
            log_action('TOKEN_EXPIRADO', details=f"IP: {request.remote_addr}", level='warning')
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError as e:
            from src.utils.logger import log_action
            log_action('TOKEN_INVALIDO', details=f"Error: {str(e)}", level='warning')
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
                os.getenv('JWT_SECRET_KEY', 'secret-key'), 
                algorithms=['HS256']
            )
            
            # Verificar que sea un token de cambio
            if not payload.get('es_token_cambio'):
                from src.utils.logger import log_action
                log_action('ACCESO_DENEGADO_CAMBIO', details="Token normal usado en endpoint de cambio", level='warning')
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
                from src.utils.logger import log_action
                log_action('PERMISO_DENEGADO', user_id=request.persona_id, 
                          details=f"Rol: {request.rol}, Requerido: {roles_permitidos}, Endpoint: {request.path}", level='warning')
                return jsonify({"error": "Permisos insuficientes"}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator