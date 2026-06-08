from flask import request, jsonify
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido
from datetime import datetime, timedelta

def asignar_horario():
    """POST /horarios - Asignar horario a un empleado (admin/supervisor)"""
    data = request.get_json()
    
    campos = ['persona_id', 'dia_semana', 'hora_inicio', 'hora_fin', 'horas_esperadas']
    for campo in campos:
        if campo not in data:
            return jsonify({"error": f"Falta campo: {campo}"}), 400
    
    sql = """
        INSERT OR REPLACE INTO horarios_empleados 
        (persona_id, dia_semana, hora_inicio, hora_fin, horas_esperadas, activo)
        VALUES (?, ?, ?, ?, ?, 1)
    """
    try:
        Database.execute_query(sql, (
            data['persona_id'], data['dia_semana'],
            data['hora_inicio'], data['hora_fin'], data['horas_esperadas']
        ))
        return jsonify({"success": True, "message": "Horario asignado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def obtener_horarios_empleado(persona_id=None):
    """GET /horarios - Obtener horarios del empleado autenticado o de uno específico"""
    if not persona_id:
        persona_id = request.persona_id
    
    sql = """
        SELECT h.*, p.nombre, p.apellido
        FROM horarios_empleados h
        JOIN personas p ON h.persona_id = p.id
        WHERE h.persona_id = ? AND h.activo = 1
        ORDER BY 
            CASE h.dia_semana
                WHEN 'lunes' THEN 1
                WHEN 'martes' THEN 2
                WHEN 'miercoles' THEN 3
                WHEN 'jueves' THEN 4
                WHEN 'viernes' THEN 5
                WHEN 'sabado' THEN 6
                WHEN 'domingo' THEN 7
            END
    """
    horarios = Database.execute_query(sql, (persona_id,), fetch_all=True)
    
    return jsonify({"success": True, "data": horarios}), 200

def calcular_horas_periodo():
    """GET /horarios/calcular - Calcular horas trabajadas en un período"""
    persona_id = request.args.get('persona_id', request.persona_id)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Se requieren fecha_inicio y fecha_fin"}), 400
    
    sql = """
        SELECT 
            SUM((strftime('%s', hora_salida) - strftime('%s', hora_entrada)) / 3600.0) as horas
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ?
            AND hora_entrada IS NOT NULL AND hora_salida IS NOT NULL
    """
    resultado = Database.execute_query(sql, (persona_id, fecha_inicio, fecha_fin), fetch_one=True)
    horas_trabajadas = round(resultado['horas'] or 0, 2)
    
    # Calcular horas esperadas según horarios
    sql_horario = """
        SELECT SUM(horas_esperadas) as total_esperadas
        FROM horarios_empleados
        WHERE persona_id = ? AND activo = 1
    """
    esperadas_result = Database.execute_query(sql_horario, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    
    return jsonify({
        "success": True,
        "data": {
            "persona_id": persona_id,
            "horas_trabajadas": horas_trabajadas,
            "horas_esperadas": horas_esperadas,
            "horas_extra": round(max(0, horas_trabajadas - horas_esperadas), 2),
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
    }), 200

def calcular_pago():
    """POST /horarios/pago - Calcular pago para un período"""
    data = request.get_json()
    persona_id = data.get('persona_id', request.persona_id)
    periodo = data.get('periodo')  # Formato: '2025-01'
    sueldo_base = data.get('sueldo_base', 1000)  # Sueldo mensual por defecto
    valor_hora_extra = data.get('valor_hora_extra', 15)  # Valor por hora extra
    
    # Parsear período
    anio, mes = map(int, periodo.split('-'))
    fecha_inicio = f"{anio}-{mes:02d}-01"
    # Último día del mes
    from calendar import monthrange
    ultimo_dia = monthrange(anio, mes)[1]
    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia}"
    
    # Obtener horas trabajadas
    sql_asistencias = """
        SELECT 
            SUM((strftime('%s', hora_salida) - strftime('%s', hora_entrada)) / 3600.0) as horas
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ?
            AND hora_entrada IS NOT NULL AND hora_salida IS NOT NULL
    """
    horas_result = Database.execute_query(sql_asistencias, (persona_id, fecha_inicio, fecha_fin), fetch_one=True)
    horas_trabajadas = round(horas_result['horas'] or 0, 2)
    
    # Obtener horas esperadas
    sql_horario = """
        SELECT SUM(horas_esperadas) as total_esperadas
        FROM horarios_empleados
        WHERE persona_id = ? AND activo = 1
    """
    esperadas_result = Database.execute_query(sql_horario, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    horas_extra = max(0, horas_trabajadas - horas_esperadas)
    
    # Calcular pago
    pago_extra = horas_extra * valor_hora_extra
    total_pagado = sueldo_base + pago_extra
    
    # Guardar en tabla pagos
    sql_insert = """
        INSERT INTO pagos (persona_id, periodo, horas_trabajadas, horas_esperadas, horas_extra,
                          sueldo_base, pago_extra, total_pagado, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
    """
    Database.execute_query(sql_insert, (persona_id, periodo, horas_trabajadas, horas_esperadas,
                                        horas_extra, sueldo_base, pago_extra, total_pagado))
    
    return jsonify({
        "success": True,
        "data": {
            "persona_id": persona_id,
            "periodo": periodo,
            "horas_trabajadas": horas_trabajadas,
            "horas_esperadas": horas_esperadas,
            "horas_extra": horas_extra,
            "sueldo_base": sueldo_base,
            "pago_extra": pago_extra,
            "total_pagado": total_pagado
        }
    }), 200