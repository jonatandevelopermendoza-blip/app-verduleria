import logging
import os
from datetime import datetime

# Directorio de logs
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configurar logger principal
logger = logging.getLogger('verduleria')
logger.setLevel(logging.INFO)

# Formato de los logs
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para archivo de logs generales
file_handler = logging.FileHandler(f'{LOG_DIR}/app.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Handler para archivo de errores
error_handler = logging.FileHandler(f'{LOG_DIR}/errors.log', encoding='utf-8')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Handler para consola (opcional, para desarrollo)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Agregar handlers
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)

def log_action(action, user_id=None, user_email=None, details=None, level='info'):
    """
    Registra una acción en el sistema
    
    Args:
        action: Nombre de la acción (ej: LOGIN, CREATE_EMPLEADO)
        user_id: ID del usuario que realizó la acción
        user_email: Email del usuario
        details: Detalles adicionales
        level: info, warning, error
    """
    log_msg = f"[{action}]"
    
    if user_id or user_email:
        log_msg += f" Usuario: {user_email or f'ID:{user_id}'}"
    
    if details:
        log_msg += f" | {details}"
    
    if level == 'info':
        logger.info(log_msg)
    elif level == 'warning':
        logger.warning(log_msg)
    elif level == 'error':
        logger.error(log_msg)

def log_error(error_msg, user_id=None, user_email=None, exception=None):
    """Registra un error con detalle de excepción"""
    log_msg = f"[ERROR] {error_msg}"
    if user_id or user_email:
        log_msg += f" | Usuario: {user_email or f'ID:{user_id}'}"
    if exception:
        log_msg += f" | Excepción: {str(exception)}"
    logger.error(log_msg)