from flask import jsonify, request
from src.core.database import Database
from datetime import datetime, timedelta
import calendar

def resumen_asistencias():
    """GET /dashboard/resumen - Estadísticas de asistencias para gráficos"""
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
    
    # Asegurar que activos no sea None
    if not activos:
        activos = {'activos': 0, 'inactivos': 0}
    
    return jsonify({
        "success": True,
        "data": {
            "roles": [{"rol": r['rol'], "cantidad": r['cantidad']} for r in roles],
            "activos": activos['activos'] if activos['activos'] else 0,
            "inactivos": activos['inactivos'] if activos['inactivos'] else 0
        }
    }), 200

def resumen_horas():
    """GET /dashboard/horas - Horas trabajadas del empleado autenticado (últimos 30 días)"""
    persona_id = request.persona_id
    
    hace_30_dias = datetime.now().date() - timedelta(days=30)
    
    sql = """
        SELECT 
            fecha,
            hora_entrada,
            hora_salida,
            (strftime('%s', hora_salida) - strftime('%s', hora_entrada)) / 3600.0 as horas
        FROM asistencias
        WHERE persona_id = ? AND fecha >= ? 
            AND hora_entrada IS NOT NULL AND hora_salida IS NOT NULL
        ORDER BY fecha
    """
    
    asistencias = Database.execute_query(sql, (persona_id, hace_30_dias), fetch_all=True)
    
    fechas = []
    horas = []
    total_horas = 0
    
    for a in asistencias:
        fechas.append(a['fecha'])
        horas_trabajadas = round(a['horas'] or 0, 1)
        horas.append(horas_trabajadas)
        total_horas += horas_trabajadas
    
    return jsonify({
        "success": True,
        "data": {
            "fechas": fechas,
            "horas": horas,
            "total_horas": round(total_horas, 1)
        }
    }), 200