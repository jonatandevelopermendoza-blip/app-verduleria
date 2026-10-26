from flask import request, jsonify
from src.core.database import Database
from datetime import datetime
import calendar

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def calcular_horas_redondeadas(hora_entrada, hora_salida):
    """Calcula las horas entre dos timestamps redondeando a 15 minutos (0.25 hs)"""
    if not hora_entrada or not hora_salida:
        return 0.0
        
    try:
        # Aseguramos formato HH:MM:SS
        fmt = '%H:%M:%S' if len(str(hora_entrada)) > 5 else '%H:%M'
        t1 = datetime.strptime(str(hora_entrada), fmt)
        t2 = datetime.strptime(str(hora_salida), fmt)
        
        # Diferencia en minutos
        diff_mins = (t2 - t1).total_seconds() / 60
        
        if diff_mins <= 0:
            return 0.0
            
        # Redondear a los 15 minutos más cercanos
        mins_redondeados = round(diff_mins / 15) * 15
        
        # Convertir a horas (ej: 90 mins -> 1.5)
        return round(mins_redondeados / 60, 2)
        
    except Exception as e:
        print(f"Error calculando horas: {e}")
        return 0.0

def obtener_dia_semana(fecha_str):
    """Convierte 'YYYY-MM-DD' al nombre del día en español"""
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        return dias[fecha.weekday()]
    except:
        return None

# ============================================
# CONTROLADORES
# ============================================

def asignar_horario():
    """POST /horarios - Asignar horario a un empleado"""
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

def obtener_horarios(persona_id=None):
    """GET /horarios - Obtener horarios"""
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
    horarios_dict = [dict(h) for h in horarios] if horarios else []

    return jsonify({"success": True, "data": horarios}), 200

def calcular_horas():
    """GET /horarios/calcular - Calcular horas trabajadas en un rango"""
    persona_id = request.args.get('persona_id', request.persona_id)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "Se requieren fecha_inicio y fecha_fin"}), 400
    
    # Traemos los registros crudos
    sql_asistencias = """
        SELECT fecha, hora_entrada, hora_salida
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ?
            AND hora_entrada IS NOT NULL
    """
    asistencias = Database.execute_query(sql_asistencias, (persona_id, fecha_inicio, fecha_fin), fetch_all=True)
    
    total_horas = 0.0
    
    for a in asistencias:
        if a['hora_salida']:
            # Si hay salida, calculamos normal
            total_horas += calcular_horas_redondeadas(a['hora_entrada'], a['hora_salida'])
        else:
            # Si no hay salida, buscamos el horario asignado para ese día
            dia = obtener_dia_semana(a['fecha'])
            if dia:
                sql_horario = """
                    SELECT horas_esperadas FROM horarios_empleados
                    WHERE persona_id = ? AND dia_semana = ? AND activo = 1
                """
                horario = Database.execute_query(sql_horario, (persona_id, dia), fetch_one=True)
                if horario:
                    total_horas += horario['horas_esperadas']
    
    # Horas esperadas totales (suma de todos los horarios activos)
    sql_horario_total = """
        SELECT SUM(horas_esperadas) as total_esperadas
        FROM horarios_empleados
        WHERE persona_id = ? AND activo = 1
    """
    esperadas_result = Database.execute_query(sql_horario_total, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    
    return jsonify({
        "success": True,
        "data": {
            "horas_trabajadas": round(total_horas, 2),
            "horas_esperadas": horas_esperadas,
            "horas_extra": round(max(0, total_horas - horas_esperadas), 2)
        }
    }), 200

def calcular_pago():
    """POST /horarios/pago - Calcular pago mensual"""
    data = request.get_json()
    persona_id = data.get('persona_id', request.persona_id)
    anio = data.get('anio', datetime.now().year)
    mes = data.get('mes', datetime.now().month)
    sueldo_base = data.get('sueldo_base', 1000)
    valor_hora_extra = data.get('valor_hora_extra', 15)
    
    fecha_inicio = f"{anio}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia}"
    
    # Traemos registros
    sql_asistencias = """
        SELECT fecha, hora_entrada, hora_salida
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ?
            AND hora_entrada IS NOT NULL
    """
    asistencias = Database.execute_query(sql_asistencias, (persona_id, fecha_inicio, fecha_fin), fetch_all=True)
    
    total_horas = 0.0
    
    for a in asistencias:
        if a['hora_salida']:
            total_horas += calcular_horas_redondeadas(a['hora_entrada'], a['hora_salida'])
        else:
            dia = obtener_dia_semana(a['fecha'])
            if dia:
                sql_horario = """
                    SELECT horas_esperadas FROM horarios_empleados
                    WHERE persona_id = ? AND dia_semana = ? AND activo = 1
                """
                horario = Database.execute_query(sql_horario, (persona_id, dia), fetch_one=True)
                if horario:
                    total_horas += horario['horas_esperadas']
    
    # Horas esperadas
    sql_horario_total = """
        SELECT SUM(horas_esperadas) as total_esperadas
        FROM horarios_empleados
        WHERE persona_id = ? AND activo = 1
    """
    esperadas_result = Database.execute_query(sql_horario_total, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    
    horas_extra = max(0, total_horas - horas_esperadas)
    pago_extra = horas_extra * valor_hora_extra
    total_pagado = sueldo_base + pago_extra
    
    return jsonify({
        "success": True,
        "data": {
            "periodo": f"{anio}-{mes:02d}",
            "horas_trabajadas": round(total_horas, 2),
            "horas_esperadas": horas_esperadas,
            "horas_extra": round(horas_extra, 2),
            "sueldo_base": sueldo_base,
            "pago_extra": round(pago_extra, 2),
            "total_pagado": round(total_pagado, 2)
        }
    }), 200