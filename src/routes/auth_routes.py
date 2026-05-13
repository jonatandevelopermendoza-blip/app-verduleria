from flask import Blueprint
from src.controllers import auth_controller
from src.middleware.auth import token_cambio_requerido

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    return auth_controller.login()

@auth_bp.route('/cambiar-password', methods=['POST'])
@token_cambio_requerido
def cambiar_password():
    return auth_controller.cambiar_password()