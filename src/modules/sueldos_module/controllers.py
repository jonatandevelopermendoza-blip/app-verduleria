from flask import request, jsonify, Response
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido
import csv
from io import StringIO
from datetime import datetime
import calendar
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


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
    """GET /sueldos/reporte - Descargar reporte de sueldos"""
    periodo = request.args.get('periodo', datetime.now().strftime('%Y-%m'))
    formato = request.args.get('formato', 'csv') # csv, xlsx, pdf
    
    # Obtener los datos de la BD
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

    # Convertir a DataFrame de Pandas
    df = pd.DataFrame(sueldos)
    
    # Agregar fila de totales
    total_row = pd.DataFrame([{
        'Empleado': 'TOTAL', 'Horas': df['Horas'].sum(), 'Extras': df['Extras'].sum(),
        'Base': df['Base'].sum(), 'Pago_Extra': df['Pago_Extra'].sum(), 'Total': df['Total'].sum()
    }])
    df = pd.concat([df, total_row], ignore_index=True)

    # --- GENERAR CSV ---
    if formato == 'csv':
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.csv'}
        )

    # --- GENERAR EXCEL (XLSX) ---
    elif formato == 'xlsx':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sueldos')
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.xlsx'}
        )

    # --- GENERAR PDF ---
    elif formato == 'pdf':
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        elements.append(Paragraph(f"Reporte de Sueldos - Período {periodo}", styles['Title']))
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Tabla
        data = [df.columns.tolist()] + df.values.tolist()
        # Formatear números a 2 decimales
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
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d1e7dd')), # Fila total verde
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=sueldos_{periodo}.pdf'}
        )