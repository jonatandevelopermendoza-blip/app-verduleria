from flask import request, jsonify
from src.config.db import Database
from datetime import datetime, date

def registrar_asistencia():
    """
    POST /asistencias/registrar
    Marca entrada o salida del empleado autenticado
    """
    # persona_id viene del token (seteado por middleware)
    persona_id = request.persona_id
    fecha_actual = date.today()
    hora_actual = datetime.now().time()
    
    # Verificar si ya existe registro para hoy
    sql_check = """
        SELECT id, hora_entrada, hora_salida 
        FROM asistencias 
        WHERE persona_id = %s AND fecha = %s
    """
    registro = Database.execute_query(sql_check, (persona_id, fecha_actual), fetch_one=True)
    
    if not registro:
        # No hay registro hoy → registrar entrada
        sql_insert = """
            INSERT INTO asistencias (persona_id, fecha, hora_entrada, estado)
            VALUES (%s, %s, %s, 'presente')
        """
        Database.execute_query(sql_insert, (persona_id, fecha_actual, hora_actual))
        
        return jsonify({
            "success": True,
            "message": f"Entrada registrada a las {hora_actual.strftime('%H:%M:%S')}"
        }), 200
    
    elif registro['hora_salida'] is None:
        # Tiene entrada pero no salida → registrar salida
        sql_update = "UPDATE asistencias SET hora_salida = %s WHERE id = %s"
        Database.execute_query(sql_update, (hora_actual, registro['id']))
        
        return jsonify({
            "success": True,
            "message": f"Salida registrada a las {hora_actual.strftime('%H:%M:%S')}"
        }), 200
    
    else:
        # Ya tiene entrada y salida
        return jsonify({
            "error": "Ya registraste entrada y salida hoy"
        }), 400

def mis_asistencias():
    """
    GET /asistencias/mis-asistencias
    Obtiene las asistencias del empleado autenticado
    """
    persona_id = request.persona_id
    
    # Parámetros opcionales: fecha desde/hasta
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    
    sql = """
        SELECT id, fecha, hora_entrada, hora_salida, estado, created_at
        FROM asistencias
        WHERE persona_id = %s
    """
    params = [persona_id]
    
    if fecha_desde:
        sql += " AND fecha >= %s"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND fecha <= %s"
        params.append(fecha_hasta)
    
    sql += " ORDER BY fecha DESC"
    
    asistencias = Database.execute_query(sql, params, fetch_all=True)
    
    # Formatear resultados
    for a in asistencias:
        a['fecha'] = a['fecha'].isoformat() if a['fecha'] else None
        a['hora_entrada'] = str(a['hora_entrada']) if a['hora_entrada'] else None
        a['hora_salida'] = str(a['hora_salida']) if a['hora_salida'] else None
    
    return jsonify({
        "success": True,
        "data": asistencias
    }), 200

def reporte_asistencias():
    """
    GET /asistencias/reporte
    Reporte general de asistencias (solo admin/supervisor)
    """
    # Verificar rol (debe venir del token)
    if request.rol not in ['admin', 'supervisor']:
        return jsonify({"error": "Permisos insuficientes"}), 403
    
    # Parámetros de filtro
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
            a.estado,
            TIMEDIFF(a.hora_salida, a.hora_entrada) as horas_trabajadas
        FROM asistencias a
        JOIN personas p ON a.persona_id = p.id
        WHERE 1=1
    """
    params = []
    
    if fecha_desde:
        sql += " AND a.fecha >= %s"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND a.fecha <= %s"
        params.append(fecha_hasta)
    if empleado_id:
        sql += " AND a.persona_id = %s"
        params.append(empleado_id)
    
    sql += " ORDER BY a.fecha DESC, p.nombre"
    
    asistencias = Database.execute_query(sql, params, fetch_all=True)
    
    # Formatear resultados
    for a in asistencias:
        a['fecha'] = a['fecha'].isoformat() if a['fecha'] else None
        a['hora_entrada'] = str(a['hora_entrada']) if a['hora_entrada'] else None
        a['hora_salida'] = str(a['hora_salida']) if a['hora_salida'] else None
        a['horas_trabajadas'] = str(a['horas_trabajadas']) if a['horas_trabajadas'] else None
    
    return jsonify({
        "success": True,
        "data": asistencias
    }), 200