from flask import request, jsonify
from src.core.database import Database

def listar_empleados():
    sql = """
        SELECT p.id, p.nombre, p.apellido, p.dni, p.email, p.rol, p.activo, p.primer_login,
               p.created_at, p.updated_at,
               u.id as usuario_id, u.ultimo_login
        FROM personas p
        LEFT JOIN usuarios u ON p.id = u.persona_id
        WHERE p.activo = 1
        ORDER BY p.id
    """
    
    empleados = Database.execute_query(sql, fetch_all=True)
    
    resultado = []
    for emp in empleados:
        resultado.append({
            "id": emp['id'],
            "nombre": emp['nombre'],
            "apellido": emp['apellido'],
            "dni": emp['dni'],
            "email": emp['email'],
            "rol": emp['rol'],
            "primer_login": bool(emp['primer_login']),
            "ultimo_login": emp['ultimo_login'],
            "created_at": emp['created_at'],
            "updated_at": emp['updated_at']
        })
    
    return jsonify({"success": True, "data": resultado}), 200