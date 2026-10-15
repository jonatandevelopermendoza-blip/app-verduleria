from flask import request, jsonify, Response
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido
import csv
from io import StringIO
from datetime import datetime
import calendar

def calcular_sueldo_empleado(persona_id, anio, mes):
    """Calcula el sueldo de un empleado para un período dado"""
    
    # Obtener configuración
    sql_config = """
        SELECT sueldo_base, valor_hora_extra 
        FROM configuracion_sueldos 
        WHERE persona_id = ? 
        ORDER BY fecha_actualizacion DESC 
        LIMIT 1
    """
    config = Database.execute_query(sql_config, (persona_id,), fetch_one=True)
    config = dict(config) if config else {'sueldo_base': 1000.0, 'valor_hora_extra': 15.0}
    
    sueldo_base = config['sueldo_base']
    valor_hora_extra = config['valor_hora_extra']
    
    # Fechas del período
    fecha_inicio = f"{anio}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia}"
    
    # Calcular horas trabajadas
    sql_horas = """
        SELECT 
            SUM((strftime('%s', hora_salida) - strftime('%s', hora_entrada)) / 3600.0) as horas
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ?
            AND hora_entrada IS NOT NULL AND hora_salida IS NOT NULL
    """
    horas_result = Database.execute_query(sql_horas, (persona_id, fecha_inicio, fecha_fin), fetch_one=True)
    horas_trabajadas = round(horas_result['horas'] or 0, 2)
    
    # Calcular horas esperadas (según horarios)
    sql_horario = """
        SELECT SUM(horas_esperadas) as total_esperadas
        FROM horarios_empleados
        WHERE persona_id = ? AND activo = 1
    """
    esperadas_result = Database.execute_query(sql_horario, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    
    # Calcular horas extra
    horas_extra = max(0, horas_trabajadas - horas_esperadas)
    pago_extra = horas_extra * valor_hora_extra
    total_pagado = sueldo_base + pago_extra
    
    # Guardar en pagos
    sql_insert = """
        INSERT OR REPLACE INTO pagos (persona_id, periodo, horas_trabajadas, horas_esperadas, horas_extra,
                                     sueldo_base, pago_extra, total_pagado, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
    """
    periodo = f"{anio}-{mes:02d}"
    Database.execute_query(sql_insert, (persona_id, periodo, horas_trabajadas, horas_esperadas,
                                        horas_extra, sueldo_base, pago_extra, total_pagado))
    
    return {
        'persona_id': persona_id,
        'periodo': periodo,
        'horas_trabajadas': horas_trabajadas,
        'horas_esperadas': horas_esperadas,
        'horas_extra': horas_extra,
        'sueldo_base': sueldo_base,
        'pago_extra': pago_extra,
        'total_pagado': total_pagado,
        'valor_hora_extra': valor_hora_extra
    }

def calcular_sueldos_periodo():
    """POST /sueldos/calcular - Calcular sueldos para todos los empleados en un período"""
    data = request.get_json()
    anio = data.get('anio', datetime.now().year)
    mes = data.get('mes', datetime.now().month)
    
    # Obtener empleados activos
    sql_empleados = "SELECT id, nombre, apellido FROM personas WHERE activo = 1"
    empleados = Database.execute_query(sql_empleados, fetch_all=True)
    
    resultados = []
    for emp in empleados:
        resultado = calcular_sueldo_empleado(emp['id'], anio, mes)
        resultado['nombre'] = emp['nombre']
        resultado['apellido'] = emp['apellido']
        resultados.append(resultado)
    
    # Calcular totales
    total_sueldos = sum(r['total_pagado'] for r in resultados)
    
    return jsonify({
        "success": True,
        "data": {
            "periodo": f"{anio}-{mes:02d}",
            "empleados": resultados,
            "totales": {
                "empleados": len(resultados),
                "total_sueldos": total_sueldos
            }
        }
    }), 200

def descargar_reporte_sueldos():
    """GET /sueldos/reporte - Descargar reporte de sueldos en CSV"""
    periodo = request.args.get('periodo', datetime.now().strftime('%Y-%m'))
    anio, mes = map(int, periodo.split('-'))
    
    # Obtener sueldos calculados para el período
    sql = """
        SELECT 
            p.id, p.nombre, p.apellido, 
            pag.horas_trabajadas, pag.horas_esperadas, pag.horas_extra,
            pag.sueldo_base, pag.pago_extra, pag.total_pagado,
            pag.estado
        FROM pagos pag
        JOIN personas p ON pag.persona_id = p.id
        WHERE pag.periodo = ?
        ORDER BY p.nombre
    """
    sueldos = Database.execute_query(sql, (periodo,), fetch_all=True)
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Cabecera
    writer.writerow([
        'Empleado', 'Horas Trabajadas', 'Horas Esperadas', 'Horas Extra',
        'Sueldo Base', 'Pago Extra', 'Total', 'Estado'
    ])
    
    for s in sueldos:
        writer.writerow([
            f"{s['nombre']} {s['apellido']}",
            s['horas_trabajadas'],
            s['horas_esperadas'],
            s['horas_extra'],
            s['sueldo_base'],
            s['pago_extra'],
            s['total_pagado'],
            s['estado']
        ])
    
    # Total
    writer.writerow([])
    writer.writerow(['TOTAL', '', '', '', '', '', sum(s['total_pagado'] for s in sueldos), ''])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.csv'}
    )