from flask import Blueprint
from src.modules.empleados_module import controllers
from src.middleware.auth import token_requerido, rol_requerido

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/', methods=['GET'])
@token_requerido
def listar_empleados():
    return controllers.listar_empleados()

@empleados_bp.route('/', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def crear_empleado():
    return controllers.crear_empleado()

@empleados_bp.route('/<int:id_empleado>', methods=['GET'])
@token_requerido
def obtener_empleado(id_empleado):
    return controllers.obtener_empleado(id_empleado)

@empleados_bp.route('/<int:id_empleado>', methods=['PUT'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def actualizar_empleado(id_empleado):
    return controllers.actualizar_empleado(id_empleado)

@empleados_bp.route('/<int:id_empleado>/rol', methods=['PUT'])
@token_requerido
@rol_requerido(['admin'])
def cambiar_rol(id_empleado):
    return controllers.cambiar_rol(id_empleado)

@empleados_bp.route('/<int:id_empleado>', methods=['DELETE'])
@token_requerido
@rol_requerido(['admin'])
def eliminar_empleado(id_empleado):
    return controllers.eliminar_empleado(id_empleado)