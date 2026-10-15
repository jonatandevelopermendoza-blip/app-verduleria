from flask import Blueprint
from src.modules.finanzas_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

finanzas_bp = Blueprint('finanzas', __name__)

@finanzas_bp.route('/resumen', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def resumen_financiero():
    return controllers.resumen_financiero()

@finanzas_bp.route('/gastos', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def listar_gastos():
    return controllers.listar_gastos()

@finanzas_bp.route('/gastos', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def crear_gasto():
    return controllers.crear_gasto()

@finanzas_bp.route('/gastos/<int:gasto_id>', methods=['DELETE'])
@token_requerido
@rol_requerido(['admin'])
def eliminar_gasto(gasto_id):
    return controllers.eliminar_gasto(gasto_id)