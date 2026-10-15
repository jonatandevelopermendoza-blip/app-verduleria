from flask import Blueprint
from src.modules.sueldos_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

sueldos_bp = Blueprint('sueldos', __name__)

@sueldos_bp.route('/calcular', methods=['POST'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def calcular_sueldos():
    return controllers.calcular_sueldos_periodo()

@sueldos_bp.route('/reporte', methods=['GET'])
@token_requerido
@rol_requerido(['admin'])
def descargar_reporte():
    return controllers.descargar_reporte_sueldos()