from flask import request, jsonify
from src.core.database import Database
from datetime import datetime, date

def registrar_asistencia():
    """POST /asistencias/registrar - Marca entrada o salida"""
    from flask import session
    persona_id = session.get('persona_id', 1)  # Temporal
    
    fecha_actual = date.today().isoformat()
    hora_actual = datetime.now().strftime('%H:%M:%S')
    
    # Verificar si ya existe registro para hoy
    sql_check = """
        SELECT id, hora_entrada, hora_salida 
        FROM asistencias 
        WHERE persona_id = ? AND fecha = ?
    """
    registro = Database.execute_query(sql_check, (persona_id, fecha_actual), fetch_one=True)
    
    if not registro:
        sql_insert = """
            INSERT INTO asistencias (persona_id, fecha, hora_entrada, estado)
            VALUES (?, ?, ?, 'presente')
        """
        Database.execute_query(sql_insert, (persona_id, fecha_actual, hora_actual))
        
        return jsonify({
            "success": True,
            "message": f"Entrada registrada a las {hora_actual}"
        }), 200
    
    elif registro['hora_salida'] is None:
        sql_update = "UPDATE asistencias SET hora_salida = ? WHERE id = ?"
        Database.execute_query(sql_update, (hora_actual, registro['id']))
        
        return jsonify({
            "success": True,
            "message": f"Salida registrada a las {hora_actual}"
        }), 200
    
    else:
        return jsonify({
            "error": "Ya registraste entrada y salida hoy"
        }), 400
    
def mis_asistencias():
    """GET /asistencias/mis-asistencias - Obtiene las asistencias del empleado"""
    persona_id = 1  # Temporal, después del token
    
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    sql = "SELECT id, fecha, hora_entrada, hora_salida, estado, created_at FROM asistencias WHERE persona_id = ?"
    params = [persona_id]
    
    if fecha_desde:
        sql += " AND fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND fecha <= ?"
        params.append(fecha_hasta)
    
    sql += " ORDER BY fecha DESC"
    
    asistencias = Database.execute_query(sql, params, fetch_all=True)
    
    resultado = []
    for a in asistencias:
        resultado.append({
            "id": a['id'],
            "fecha": a['fecha'],
            "hora_entrada": a['hora_entrada'],
            "hora_salida": a['hora_salida'],
            "estado": a['estado'],
            "created_at": a['created_at']
        })
    
    return jsonify({"success": True, "data": resultado}), 200

def reporte_asistencias():
    """GET /asistencias/reporte - Reporte general (solo admin)"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    empleado_id = request.args.get('empleado_id')
    
    sql = """
        SELECT 
            p.id as persona_id,
            p.nombre,
            p.apellido,
            a.fecha,
            a.hora_entrada,
            a.hora_salida,
            a.estado
        FROM asistencias a
        JOIN personas p ON a.persona_id = p.id
        WHERE 1=1
    """
    params = []
    
    if fecha_desde:
        sql += " AND a.fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND a.fecha <= ?"
        params.append(fecha_hasta)
    if empleado_id:
        sql += " AND a.persona_id = ?"
        params.append(empleado_id)
    
    sql += " ORDER BY a.fecha DESC, p.nombre"
    
    asistencias = Database.execute_query(sql, params, fetch_all=True)
    
    resultado = []
    for a in asistencias:
        resultado.append({
            "persona_id": a['persona_id'],
            "nombre": a['nombre'],
            "apellido": a['apellido'],
            "fecha": a['fecha'],
            "hora_entrada": a['hora_entrada'],
            "hora_salida": a['hora_salida'],
            "estado": a['estado']
        })
    
    return jsonify({"success": True, "data": resultado}), 200