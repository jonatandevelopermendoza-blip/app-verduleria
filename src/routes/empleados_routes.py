from flask import Blueprint, request
from src.controllers import empleados_controller
from src.middleware.auth import token_requerido, rol_requerido

empleados_bp = Blueprint('empleados', __name__)

@empleados_bp.route('/', methods=['GET'])
@token_requerido
def listar_empleados():
    """Cualquier rol autenticado puede listar empleados"""
    return empleados_controller.listar_empleados()

@empleados_bp.route('/<int:id_empleado>', methods=['GET'])
@token_requerido
def obtener_empleado(id_empleado):
    """Cualquier rol autenticado puede ver detalles"""
    return empleados_controller.obtener_empleado(id_empleado)

@empleados_bp.route('/', methods=['POST'])
@token_requerido
@rol_requerido(['admin'])
def crear_empleado():
    """Solo admin puede crear empleados"""
    return empleados_controller.crear_empleado()

@empleados_bp.route('/<int:id_empleado>', methods=['PUT'])
@token_requerido
@rol_requerido(['admin', 'supervisor'])
def actualizar_empleado(id_empleado):
    """Admin o supervisor pueden actualizar datos básicos"""
    return empleados_controller.actualizar_empleado(id_empleado)

@empleados_bp.route('/<int:id_empleado>/rol', methods=['PUT'])
@token_requerido
@rol_requerido(['admin'])
def cambiar_rol(id_empleado):
    """Solo admin puede cambiar roles"""
    return empleados_controller.cambiar_rol(id_empleado)

@empleados_bp.route('/<int:id_empleado>', methods=['DELETE'])
@token_requerido
@rol_requerido(['admin'])
def eliminar_empleado(id_empleado):
    """Solo admin puede dar de baja (lógica)"""
    return empleados_controller.eliminar_empleado(id_empleado)