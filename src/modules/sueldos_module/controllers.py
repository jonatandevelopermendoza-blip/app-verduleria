from flask import request, jsonify, Response
from src.core.database import Database
from datetime import datetime
import calendar
import csv
from io import BytesIO, StringIO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def calcular_horas_redondeadas(hora_entrada, hora_salida):
    """Calcula las horas entre dos timestamps redondeando a 15 minutos"""
    if not hora_entrada or not hora_salida:
        return 0.0
    try:
        fmt = '%H:%M:%S' if len(str(hora_entrada)) > 5 else '%H:%M'
        t1 = datetime.strptime(str(hora_entrada), fmt)
        t2 = datetime.strptime(str(hora_salida), fmt)
        diff_mins = (t2 - t1).total_seconds() / 60
        if diff_mins <= 0: return 0.0
        mins_redondeados = round(diff_mins / 15) * 15
        return round(mins_redondeados / 60, 2)
    except:
        return 0.0

def obtener_dia_semana(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        return dias[fecha.weekday()]
    except:
        return None

# ============================================
# CONTROLADORES
# ============================================

def calcular_sueldo_empleado(persona_id, anio, mes):
    """Calcula el sueldo de un empleado para un período dado"""
    sql_config = """
        SELECT sueldo_base, valor_hora_extra 
        FROM configuracion_sueldos 
        WHERE persona_id = ? 
        ORDER BY fecha_actualizacion DESC LIMIT 1
    """
    config = Database.execute_query(sql_config, (persona_id,), fetch_one=True)
    config = dict(config) if config else {'sueldo_base': 1000.0, 'valor_hora_extra': 15.0}
    
    sueldo_base = config['sueldo_base']
    valor_hora_extra = config['valor_hora_extra']
    
    fecha_inicio = f"{anio}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    fecha_fin = f"{anio}-{mes:02d}-{ultimo_dia}"
    
    # Traemos registros
    sql_asistencias = """
        SELECT fecha, hora_entrada, hora_salida
        FROM asistencias
        WHERE persona_id = ? AND fecha BETWEEN ? AND ? AND hora_entrada IS NOT NULL
    """
    asistencias = Database.execute_query(sql_asistencias, (persona_id, fecha_inicio, fecha_fin), fetch_all=True)
    
    total_horas = 0.0
    
    for a in asistencias:
        if a['hora_salida']:
            total_horas += calcular_horas_redondeadas(a['hora_entrada'], a['hora_salida'])
        else:
            dia = obtener_dia_semana(a['fecha'])
            if dia:
                sql_horario = "SELECT horas_esperadas FROM horarios_empleados WHERE persona_id = ? AND dia_semana = ? AND activo = 1"
                horario = Database.execute_query(sql_horario, (persona_id, dia), fetch_one=True)
                if horario:
                    total_horas += horario['horas_esperadas']
    
    # Horas esperadas
    sql_horario_total = "SELECT SUM(horas_esperadas) as total_esperadas FROM horarios_empleados WHERE persona_id = ? AND activo = 1"
    esperadas_result = Database.execute_query(sql_horario_total, (persona_id,), fetch_one=True)
    horas_esperadas = esperadas_result['total_esperadas'] or 0
    
    horas_extra = max(0, total_horas - horas_esperadas)
    pago_extra = horas_extra * valor_hora_extra
    total_pagado = sueldo_base + pago_extra
    
    # Guardar en pagos
    sql_insert = """
        INSERT OR REPLACE INTO pagos (persona_id, periodo, horas_trabajadas, horas_esperadas, horas_extra,
                                     sueldo_base, pago_extra, total_pagado, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
    """
    periodo = f"{anio}-{mes:02d}"
    Database.execute_query(sql_insert, (persona_id, periodo, round(total_horas, 2), horas_esperadas,
                                        round(horas_extra, 2), sueldo_base, round(pago_extra, 2), round(total_pagado, 2)))
    
    return {
        'persona_id': persona_id,
        'periodo': periodo,
        'horas_trabajadas': round(total_horas, 2),
        'horas_esperadas': horas_esperadas,
        'horas_extra': round(horas_extra, 2),
        'sueldo_base': sueldo_base,
        'pago_extra': round(pago_extra, 2),
        'total_pagado': round(total_pagado, 2)
    }

def calcular_sueldos_periodo():
    """POST /sueldos/calcular - Calcular sueldos para todos los empleados"""
    data = request.get_json()
    anio = data.get('anio', datetime.now().year)
    mes = data.get('mes', datetime.now().month)
    
    sql_empleados = "SELECT id, nombre, apellido FROM personas WHERE activo = 1"
    empleados = Database.execute_query(sql_empleados, fetch_all=True)
    
    resultados = []
    for emp in empleados:
        resultado = calcular_sueldo_empleado(emp['id'], anio, mes)
        resultado['nombre'] = emp['nombre']
        resultado['apellido'] = emp['apellido']
        resultados.append(resultado)
    
    total_sueldos = sum(r['total_pagado'] for r in resultados)
    
    return jsonify({
        "success": True,
        "data": {
            "periodo": f"{anio}-{mes:02d}",
            "empleados": resultados,
            "totales": {
                "empleados": len(resultados),
                "total_sueldos": round(total_sueldos, 2)
            }
        }
    }), 200

def descargar_reporte_sueldos():
    """GET /sueldos/reporte - Descargar reporte de sueldos"""
    periodo = request.args.get('periodo', datetime.now().strftime('%Y-%m'))
    formato = request.args.get('formato', 'csv')
    
    sql = """
        SELECT 
            p.nombre || ' ' || p.apellido as Empleado,
            pag.horas_trabajadas as Horas,
            pag.horas_extra as Extras,
            pag.sueldo_base as Base,
            pag.pago_extra as Pago_Extra,
            pag.total_pagado as Total
        FROM pagos pag
        JOIN personas p ON pag.persona_id = p.id
        WHERE pag.periodo = ?
        ORDER BY p.nombre
    """
    sueldos = Database.execute_query(sql, (periodo,), fetch_all=True)
    
    if not sueldos:
        return jsonify({"error": "No hay datos para este período"}), 404

    df = pd.DataFrame(sueldos)
    
    total_row = pd.DataFrame([{
        'Empleado': 'TOTAL', 'Horas': df['Horas'].sum(), 'Extras': df['Extras'].sum(),
        'Base': df['Base'].sum(), 'Pago_Extra': df['Pago_Extra'].sum(), 'Total': df['Total'].sum()
    }])
    df = pd.concat([df, total_row], ignore_index=True)

    if formato == 'csv':
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        return Response(output.getvalue(), mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.csv'})

    elif formato == 'xlsx':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sueldos')
        output.seek(0)
        return Response(output.getvalue(), mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.xlsx'})

    elif formato == 'pdf':
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"Reporte de Sueldos - Período {periodo}", styles['Title']))
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        data = [df.columns.tolist()] + df.values.tolist()
        for i in range(1, len(data)):
            for j in range(3, 6):
                data[i][j] = f"${data[i][j]:.2f}"
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d1e7dd')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        return Response(output.getvalue(), mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.pdf'})