from flask import request, jsonify
from src.config.db import Database

def listar_empleados():
    """GET /empleados - Lista todos los empleados activos (baja lógica)"""
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
    
    # Agrupar por empleado (por si tienen múltiples usuarios, aunque ahora sea 1 a 1)
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
            "ultimo_login": emp['ultimo_login'].isoformat() if emp['ultimo_login'] else None,
            "created_at": emp['created_at'].isoformat() if emp['created_at'] else None,
            "updated_at": emp['updated_at'].isoformat() if emp['updated_at'] else None
        })
    
    return jsonify({"success": True, "data": resultado}), 200

def obtener_empleado(id_empleado):
    """GET /empleados/{id} - Obtener detalle de un empleado específico"""
    sql = """
        SELECT p.id, p.nombre, p.apellido, p.dni, p.email, p.rol, p.activo, p.primer_login,
               p.created_at, p.updated_at,
               u.id as usuario_id, u.ultimo_login
        FROM personas p
        LEFT JOIN usuarios u ON p.id = u.persona_id
        WHERE p.id = %s
    """
    
    empleado = Database.execute_query(sql, (id_empleado,), fetch_one=True)
    
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    resultado = {
        "id": empleado['id'],
        "nombre": empleado['nombre'],
        "apellido": empleado['apellido'],
        "dni": empleado['dni'],
        "email": empleado['email'],
        "rol": empleado['rol'],
        "activo": bool(empleado['activo']),
        "primer_login": bool(empleado['primer_login']),
        "ultimo_login": empleado['ultimo_login'].isoformat() if empleado['ultimo_login'] else None,
        "created_at": empleado['created_at'].isoformat() if empleado['created_at'] else None,
        "updated_at": empleado['updated_at'].isoformat() if empleado['updated_at'] else None
    }
    
    return jsonify({"success": True, "data": resultado}), 200

def crear_empleado():
    """POST /empleados - Crear nuevo empleado (solo admin)"""
    data = request.get_json()
    
    # Validaciones básicas
    campos_requeridos = ['nombre', 'apellido', 'dni', 'email', 'rol']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta campo requerido: {campo}"}), 400
    
    # Validar rol válido
    if data['rol'] not in ['admin', 'supervisor', 'empleado']:
        return jsonify({"error": "Rol inválido. Debe ser: admin, supervisor o empleado"}), 400
    
    # Contraseña por defecto (debe cambiarse en primer login)
    from src.controllers.auth_controller import hash_password
    password_hash = hash_password('cambiar123')
    
    connection = Database.get_connection()
    try:
        with connection.cursor() as cursor:
            # Insertar en personas
            sql_personas = """
                INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_personas, (
                data['nombre'], data['apellido'], data['dni'],
                data['email'], data['rol'], 1, 1
            ))
            persona_id = cursor.lastrowid
            
            # Insertar en usuarios
            sql_usuarios = """
                INSERT INTO usuarios (persona_id, password_hash, ultimo_login)
                VALUES (%s, %s, NULL)
            """
            cursor.execute(sql_usuarios, (persona_id, password_hash))
            
            connection.commit()
            
            return jsonify({
                "success": True,
                "message": "Empleado creado correctamente",
                "id": persona_id
            }), 201
            
    except Exception as e:
        connection.rollback()
        # Error por DNI o email duplicado
        if "Duplicate entry" in str(e):
            return jsonify({"error": "El DNI o email ya existe"}), 400
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
        
def actualizar_empleado(id_empleado):
    """PUT /empleados/{id} - Actualizar datos de un empleado"""
    data = request.get_json()
    
    # Verificar que el empleado existe
    check_sql = "SELECT id FROM personas WHERE id = %s"
    existe = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    if not existe:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    # Construir SET dinámico según campos enviados
    campos_actualizables = ['nombre', 'apellido', 'dni', 'email']
    updates = []
    valores = []
    
    for campo in campos_actualizables:
        if campo in data:
            updates.append(f"{campo} = %s")
            valores.append(data[campo])
    
    if not updates:
        return jsonify({"error": "No hay campos para actualizar"}), 400
    
    valores.append(id_empleado)
    sql = f"UPDATE personas SET {', '.join(updates)} WHERE id = %s"
    Database.execute_query(sql, valores)
    
    return jsonify({"success": True, "message": "Empleado actualizado correctamente"}), 200

def cambiar_rol(id_empleado):
    """PUT /empleados/{id}/rol - Cambiar rol de un empleado (solo admin)"""
    data = request.get_json()
    
    if 'rol' not in data:
        return jsonify({"error": "Se requiere el campo 'rol'"}), 400
    
    nuevo_rol = data['rol']
    if nuevo_rol not in ['admin', 'supervisor', 'empleado']:
        return jsonify({"error": "Rol inválido"}), 400
    
    # Verificar existencia
    check_sql = "SELECT id FROM personas WHERE id = %s"
    existe = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    if not existe:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    sql = "UPDATE personas SET rol = %s WHERE id = %s"
    Database.execute_query(sql, (nuevo_rol, id_empleado))
    
    return jsonify({"success": True, "message": f"Rol actualizado a {nuevo_rol}"}), 200

def eliminar_empleado(id_empleado):
    """DELETE /empleados/{id} - Baja lógica (activo = 0)"""
    # Verificar existencia
    check_sql = "SELECT id, activo FROM personas WHERE id = %s"
    empleado = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    if empleado['activo'] == 0:
        return jsonify({"error": "El empleado ya está dado de baja"}), 400
    
    sql = "UPDATE personas SET activo = 0 WHERE id = %s"
    Database.execute_query(sql, (id_empleado,))
    
    return jsonify({"success": True, "message": "Empleado dado de baja correctamente"}), 200