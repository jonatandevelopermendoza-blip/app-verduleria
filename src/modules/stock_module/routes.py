from flask import Blueprint
from src.modules.stock_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

stock_bp = Blueprint('stock', __name__)

# Categorías
@stock_bp.route('/categorias', methods=['GET'])
@token_requerido
def listar_categorias():
    return controllers.listar_categorias()

@stock_bp.route('/categorias', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def crear_categoria():
    return controllers.crear_categoria()

# Productos
@stock_bp.route('/productos', methods=['GET'])
@token_requerido
def listar_productos():
    return controllers.listar_productos()

@stock_bp.route('/productos', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def crear_producto():
    return controllers.crear_producto()

# Movimientos
@stock_bp.route('/movimientos', methods=['POST'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def actualizar_stock():
    return controllers.actualizar_stock()

@stock_bp.route('/alertas', methods=['GET'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def stock_bajo():
    return controllers.stock_bajo()