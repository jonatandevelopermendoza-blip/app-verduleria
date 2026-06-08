from flask import Blueprint
from src.modules.asistencias_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/registrar', methods=['POST'])
@token_requerido
def registrar_asistencia():
    return controllers.registrar_asistencia()

@asistencias_bp.route('/mis-asistencias', methods=['GET'])
@token_requerido
def mis_asistencias():
    return controllers.mis_asistencias()

@asistencias_bp.route('/reporte', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def reporte_asistencias():
    return controllers.reporte_asistencias()