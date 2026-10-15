from flask import request, jsonify
from src.core.database import Database
from datetime import datetime, timedelta

def resumen_financiero():
    """GET /finanzas/resumen - Resumen de ingresos, egresos y balance"""
    periodo = request.args.get('periodo', 'mensual')  # diario, semanal, mensual, anual
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    # Si no se especifican fechas, calcular según período
    hoy = datetime.now().date()
    if not fecha_fin:
        fecha_fin = hoy.isoformat()
    
    if not fecha_inicio:
        if periodo == 'diario':
            fecha_inicio = hoy.isoformat()
        elif periodo == 'semanal':
            fecha_inicio = (hoy - timedelta(days=7)).isoformat()
        elif periodo == 'mensual':
            fecha_inicio = (hoy - timedelta(days=30)).isoformat()
        elif periodo == 'anual':
            fecha_inicio = (hoy - timedelta(days=365)).isoformat()
        else:
            fecha_inicio = (hoy - timedelta(days=30)).isoformat()
    
    # 1. Ingresos por ventas
    sql_ventas = """
        SELECT 
            COALESCE(SUM(total), 0) as total_ingresos,
            COUNT(*) as cantidad_ventas,
            COALESCE(AVG(total), 0) as ticket_promedio
        FROM ventas
        WHERE date(fecha) BETWEEN ? AND ?
    """
    ingresos = Database.execute_query(sql_ventas, (fecha_inicio, fecha_fin), fetch_one=True)
    
    # 2. Egresos por sueldos (pagos)
    sql_sueldos = """
        SELECT COALESCE(SUM(total_pagado), 0) as total_sueldos
        FROM pagos
        WHERE created_at BETWEEN ? AND ?
    """
    sueldos = Database.execute_query(sql_sueldos, (fecha_inicio, fecha_fin), fetch_one=True)
    
    # 3. Egresos por compras a proveedores (movimientos stock tipo 'entrada')
    sql_compras = """
        SELECT COALESCE(SUM(m.cantidad * p.precio_compra), 0) as total_compras
        FROM movimientos_stock m
        JOIN productos p ON m.producto_id = p.id
        WHERE m.tipo = 'entrada' AND date(m.created_at) BETWEEN ? AND ?
    """
    compras = Database.execute_query(sql_compras, (fecha_inicio, fecha_fin), fetch_one=True)
    
    # 4. Gastos generales
    sql_gastos = """
        SELECT 
            COALESCE(SUM(monto), 0) as total_gastos,
            categoria,
            COUNT(*) as cantidad
        FROM gastos_generales
        WHERE date(fecha) BETWEEN ? AND ?
        GROUP BY categoria
    """
    gastos_generales = Database.execute_query(sql_gastos, (fecha_inicio, fecha_fin), fetch_all=True)
    
    sql_gastos_total = """
        SELECT COALESCE(SUM(monto), 0) as total_gastos
        FROM gastos_generales
        WHERE date(fecha) BETWEEN ? AND ?
    """
    gastos_total = Database.execute_query(sql_gastos_total, (fecha_inicio, fecha_fin), fetch_one=True)
    
    total_egresos = (sueldos['total_sueldos'] or 0) + (compras['total_compras'] or 0) + (gastos_total['total_gastos'] or 0)
    balance = (ingresos['total_ingresos'] or 0) - total_egresos
    
    return jsonify({
        "success": True,
        "data": {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "ingresos": {
                "total": ingresos['total_ingresos'],
                "cantidad_ventas": ingresos['cantidad_ventas'],
                "ticket_promedio": round(ingresos['ticket_promedio'], 2)
            },
            "egresos": {
                "sueldos": sueldos['total_sueldos'],
                "compras_proveedores": compras['total_compras'],
                "gastos_generales": gastos_total['total_gastos'],
                "total": total_egresos,
                "detalle_gastos": gastos_generales
            },
            "balance": balance,
            "margen_ganancia": round((balance / ingresos['total_ingresos'] * 100), 2) if ingresos['total_ingresos'] > 0 else 0
        }
    }), 200

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