from flask import jsonify
from src.core.database import Database
from datetime import datetime, timedelta

def resumen_asistencias():
    """GET /dashboard/resumen - Estadísticas de asistencias para gráficos"""
    # Últimos 7 días
    hoy = datetime.now().date()
    hace_7_dias = hoy - timedelta(days=7)
    
    sql = """
        SELECT 
            fecha,
            COUNT(*) as total,
            SUM(CASE WHEN hora_entrada IS NOT NULL THEN 1 ELSE 0 END) as con_entrada,
            SUM(CASE WHEN hora_salida IS NOT NULL THEN 1 ELSE 0 END) as con_salida
        FROM asistencias
        WHERE fecha >= ?
        GROUP BY fecha
        ORDER BY fecha
    """
    
    resultados = Database.execute_query(sql, (hace_7_dias,), fetch_all=True)
    
    fechas = []
    entradas = []
    salidas = []
    
    for r in resultados:
        fechas.append(r['fecha'])
        entradas.append(r['con_entrada'])
        salidas.append(r['con_salida'])
    
    return jsonify({
        "success": True,
        "data": {
            "fechas": fechas,
            "entradas": entradas,
            "salidas": salidas
        }
    }), 200

def resumen_empleados():
    """GET /dashboard/empleados - Estadísticas de empleados"""
    sql_roles = """
        SELECT rol, COUNT(*) as cantidad
        FROM personas
        WHERE activo = 1
        GROUP BY rol
    """
    
    roles = Database.execute_query(sql_roles, fetch_all=True)
    
    sql_activos = """
        SELECT 
            SUM(CASE WHEN activo = 1 THEN 1 ELSE 0 END) as activos,
            SUM(CASE WHEN activo = 0 THEN 1 ELSE 0 END) as inactivos
        FROM personas
    """
    
    activos = Database.execute_query(sql_activos, fetch_one=True)
    
    return jsonify({
        "success": True,
        "data": {
            "roles": [{"rol": r['rol'], "cantidad": r['cantidad']} for r in roles],
            "activos": activos['activos'] if activos else 0,
            "inactivos": activos['inactivos'] if activos else 0
        }
    }), 200

def resumen_horas_empleado(empleado_id=None):
    """GET /dashboard/horas - Horas trabajadas por empleado (últimos 30 días)"""
    from flask import request
    persona_id = empleado_id or request.persona_id
    
    hace_30_dias = datetime.now().date() - timedelta(days=30)
    
    sql = """
        SELECT 
            p.nombre,
            p.apellido,
            a.fecha,
            a.hora_entrada,
            a.hora_salida,
            (strftime('%s', a.hora_salida) - strftime('%s', a.hora_entrada)) / 3600.0 as horas
        FROM asistencias a
        JOIN personas p ON a.persona_id = p.id
        WHERE a.persona_id = ? AND a.fecha >= ? AND a.hora_entrada IS NOT NULL AND a.hora_salida IS NOT NULL
        ORDER BY a.fecha
    """
    
    asistencias = Database.execute_query(sql, (persona_id, hace_30_dias), fetch_all=True)
    
    fechas = []
    horas = []
    total_horas = 0
    
    for a in asistencias:
        fechas.append(a['fecha'])
        horas.append(round(a['horas'] or 0, 1))
        total_horas += (a['horas'] or 0)
    
    return jsonify({
        "success": True,
        "data": {
            "fechas": fechas,
            "horas": horas,
            "total_horas": round(total_horas, 1)
        }
    }), 200