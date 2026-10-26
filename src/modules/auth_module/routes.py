from flask import Blueprint
from src.modules.auth_module import controllers
from src.core.app import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # <-- Límite estricto en el login
def login():
    return controllers.login()

@auth_bp.route('/cambiar-password', methods=['POST'])  
def cambiar_password():
    return controllers.cambiar_password()