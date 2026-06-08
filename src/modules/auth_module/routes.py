from flask import Blueprint
from src.modules.auth_module import controllers

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    return controllers.login()