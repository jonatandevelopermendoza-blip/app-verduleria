from flask import Blueprint
from src.modules.horarios_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

horarios_bp = Blueprint('horarios', __name__)

@horarios_bp.route('/', methods=['GET'])
@token_requerido
def obtener_horarios():
    """Obtener horarios del empleado autenticado"""
    return controllers.obtener_horarios_empleado()

@horarios_bp.route('/empleado/<int:persona_id>', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def obtener_horarios_empleado(persona_id):
    """Admin/supervisor ver horarios de otro empleado"""
    return controllers.obtener_horarios_empleado(persona_id)

@horarios_bp.route('/', methods=['POST'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def asignar_horario():
    return controllers.asignar_horario()

@horarios_bp.route('/calcular', methods=['GET'])
@token_requerido
def calcular_horas():
    return controllers.calcular_horas_periodo()

@horarios_bp.route('/pago', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def calcular_pago():
    return controllers.calcular_pago()