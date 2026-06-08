from flask import Blueprint
from src.modules.empleados_module import controllers

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/', methods=['GET'])
def listar_empleados():
    return controllers.listar_empleados()