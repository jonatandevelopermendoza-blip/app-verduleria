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

def crear_empleado():
    """POST /empleados - Crear nuevo empleado (solo admin)"""
    data = request.get_json()
    
    campos_requeridos = ['nombre', 'apellido', 'dni', 'email', 'rol']
    for campo in campos_requeridos:
        if campo not in data:
            return jsonify({"error": f"Falta campo requerido: {campo}"}), 400
    
    if data['rol'] not in ['admin', 'supervisor', 'empleado']:
        return jsonify({"error": "Rol inválido"}), 400
    
    from src.modules.auth_module.controllers import hash_password
    password_hash = hash_password('cambiar123')
    
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data['nombre'], data['apellido'], data['dni'], data['email'], data['rol'], 1, 1))
        
        persona_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO usuarios (persona_id, password_hash) VALUES (?, ?)",
            (persona_id, password_hash)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Empleado creado correctamente",
            "id": persona_id
        }), 201
        
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return jsonify({"error": "El DNI o email ya existe"}), 400
        return jsonify({"error": str(e)}), 500

def obtener_empleado(id_empleado):
    """GET /empleados/{id} - Obtener detalle de un empleado"""
    sql = """
        SELECT p.id, p.nombre, p.apellido, p.dni, p.email, p.rol, p.activo, p.primer_login,
               p.created_at, p.updated_at,
               u.id as usuario_id, u.ultimo_login
        FROM personas p
        LEFT JOIN usuarios u ON p.id = u.persona_id
        WHERE p.id = ?
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
        "ultimo_login": empleado['ultimo_login'],
        "created_at": empleado['created_at'],
        "updated_at": empleado['updated_at']
    }
    
    return jsonify({"success": True, "data": resultado}), 200

def actualizar_empleado(id_empleado):
    """PUT /empleados/{id} - Actualizar datos básicos"""
    data = request.get_json()
    
    check_sql = "SELECT id FROM personas WHERE id = ?"
    existe = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    if not existe:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    campos_actualizables = ['nombre', 'apellido', 'dni', 'email']
    updates = []
    valores = []
    
    for campo in campos_actualizables:
        if campo in data:
            updates.append(f"{campo} = ?")
            valores.append(data[campo])
    
    if not updates:
        return jsonify({"error": "No hay campos para actualizar"}), 400
    
    valores.append(id_empleado)
    sql = f"UPDATE personas SET {', '.join(updates)} WHERE id = ?"
    Database.execute_query(sql, valores)
    
    return jsonify({"success": True, "message": "Empleado actualizado correctamente"}), 200

def cambiar_rol(id_empleado):
    """PUT /empleados/{id}/rol - Cambiar rol de un empleado"""
    data = request.get_json()
    
    if 'rol' not in data:
        return jsonify({"error": "Se requiere el campo 'rol'"}), 400
    
    nuevo_rol = data['rol']
    if nuevo_rol not in ['admin', 'supervisor', 'empleado']:
        return jsonify({"error": "Rol inválido"}), 400
    
    check_sql = "SELECT id FROM personas WHERE id = ?"
    existe = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    if not existe:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    sql = "UPDATE personas SET rol = ? WHERE id = ?"
    Database.execute_query(sql, (nuevo_rol, id_empleado))
    
    return jsonify({"success": True, "message": f"Rol actualizado a {nuevo_rol}"}), 200

def eliminar_empleado(id_empleado):
    """DELETE /empleados/{id} - Baja lógica"""
    check_sql = "SELECT id, activo FROM personas WHERE id = ?"
    empleado = Database.execute_query(check_sql, (id_empleado,), fetch_one=True)
    
    if not empleado:
        return jsonify({"error": "Empleado no encontrado"}), 404
    
    if empleado['activo'] == 0:
        return jsonify({"error": "El empleado ya está dado de baja"}), 400
    
    sql = "UPDATE personas SET activo = 0 WHERE id = ?"
    Database.execute_query(sql, (id_empleado,))
    
    return jsonify({"success": True, "message": "Empleado dado de baja correctamente"}), 200