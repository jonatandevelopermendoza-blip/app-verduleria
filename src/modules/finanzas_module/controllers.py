from flask import request, jsonify
from src.core.database import Database
from datetime import datetime, timedelta

def resumen_financiero():
    periodo = request.args.get('periodo', 'mensual')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # ... cálculo de fechas ...
    
    # Ingresos con discriminación de IVA
    sql_ventas = """
        SELECT 
            COALESCE(SUM(subtotal), 0) as total_neto,
            COALESCE(SUM(iva), 0) as total_iva,
            COALESCE(SUM(total), 0) as total_bruto,
            COUNT(*) as cantidad_ventas,
            COALESCE(AVG(total), 0) as ticket_promedio
        FROM ventas
        WHERE date(fecha) BETWEEN ? AND ?
    """
    ingresos = Database.execute_query(sql_ventas, (fecha_inicio, fecha_fin), fetch_one=True)
    ingresos = dict(ingresos) if ingresos else {'total_neto': 0, 'total_iva': 0, 'total_bruto': 0, 'cantidad_ventas': 0, 'ticket_promedio': 0}
    
    # ... resto del resumen ...
    
    return jsonify({
        "success": True,
        "data": {
            "ingresos": {
                "neto": ingresos['total_neto'],
                "iva": ingresos['total_iva'],
                "bruto": ingresos['total_bruto'],
                "cantidad_ventas": ingresos['cantidad_ventas'],
                "ticket_promedio": round(ingresos['ticket_promedio'], 2)
            },
            # ... más campos ...
        }
    })


def listar_gastos():
    """GET /finanzas/gastos - Listar gastos generales"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    categoria = request.args.get('categoria')
    
    sql = "SELECT * FROM gastos_generales WHERE 1=1"
    params = []
    
    if fecha_desde:
        sql += " AND fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND fecha <= ?"
        params.append(fecha_hasta)
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    
    sql += " ORDER BY fecha DESC"
    
    gastos = Database.execute_query(sql, params, fetch_all=True)
    return jsonify({"success": True, "data": gastos}), 200

def crear_gasto():
    """POST /finanzas/gastos - Registrar gasto general"""
    data = request.get_json()
    
    campos = ['concepto', 'monto', 'fecha']
    for campo in campos:
        if campo not in data:
            return jsonify({"error": f"Falta campo: {campo}"}), 400
    
    sql = """
        INSERT INTO gastos_generales (concepto, descripcion, monto, fecha, categoria, comprobante)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    Database.execute_query(sql, (
        data['concepto'],
        data.get('descripcion', ''),
        data['monto'],
        data['fecha'],
        data.get('categoria', 'operativo'),
        data.get('comprobante')
    ))
    
    return jsonify({"success": True, "message": "Gasto registrado correctamente"}), 201

def eliminar_gasto(gasto_id):
    """DELETE /finanzas/gastos/<id> - Eliminar gasto"""
    Database.execute_query("DELETE FROM gastos_generales WHERE id = ?", (gasto_id,))
    return jsonify({"success": True, "message": "Gasto eliminado"}), 200