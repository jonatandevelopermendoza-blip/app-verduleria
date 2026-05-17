from flask import Blueprint
from src.controllers import asistencias_controller
from src.middleware.auth import token_requerido, rol_requerido

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/registrar', methods=['POST'])
@token_requerido
def registrar_asistencia():
    """Cualquier empleado autenticado puede registrar entrada/salida"""
    return asistencias_controller.registrar_asistencia()

@asistencias_bp.route('/mis-asistencias', methods=['GET'])
@token_requerido
def mis_asistencias():
    """Cada empleado ve sus propias asistencias"""
    return asistencias_controller.mis_asistencias()

@asistencias_bp.route('/reporte', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def reporte_asistencias():
    """Solo admin o supervisor pueden ver el reporte general"""
    return asistencias_controller.reporte_asistencias()