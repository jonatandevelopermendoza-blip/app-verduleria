from flask import Blueprint
from src.modules.ventas_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/', methods=['POST'])
@token_requerido
def registrar_venta():
    """Cualquier empleado autenticado puede registrar ventas"""
    return controllers.registrar_venta()

@ventas_bp.route('/', methods=['GET'])
@token_requerido
def listar_ventas():
    return controllers.listar_ventas()

@ventas_bp.route('/<int:venta_id>', methods=['GET'])
@token_requerido
def detalle_venta(venta_id):
    return controllers.detalle_venta(venta_id)

@ventas_bp.route('/reporte/dia', methods=['GET'])
@token_requerido
def ventas_dia():
    return controllers.ventas_dia()