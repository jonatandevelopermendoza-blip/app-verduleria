from flask import Blueprint
from src.modules.asistencias_module import controllers

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/registrar', methods=['POST'])
def registrar_asistencia():
    return controllers.registrar_asistencia()

@asistencias_bp.route('/mis-asistencias', methods=['GET'])
def mis_asistencias():
    return controllers.mis_asistencias()

@asistencias_bp.route('/reporte', methods=['GET'])
def reporte_asistencias():
    return controllers.reporte_asistencias()