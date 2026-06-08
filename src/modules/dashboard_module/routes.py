from flask import Blueprint
from src.modules.dashboard_module import controllers
from src.middleware.auth import token_requerido

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/resumen', methods=['GET'])
@token_requerido
def resumen_asistencias():
    return controllers.resumen_asistencias()

@dashboard_bp.route('/empleados', methods=['GET'])
@token_requerido
def resumen_empleados():
    return controllers.resumen_empleados()

@dashboard_bp.route('/horas', methods=['GET'])
@token_requerido
def resumen_horas():
    return controllers.resumen_horas()