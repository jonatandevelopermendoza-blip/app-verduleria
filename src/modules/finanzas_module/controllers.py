from flask import request, jsonify
from src.core.database import Database
from datetime import datetime, timedelta

def resumen_financiero():
    """GET /finanzas/resumen - Resumen de ingresos, egresos y balance"""
    periodo = request.args.get('periodo', 'mensual')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
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
    
    # 1. Ingresos (con IVA discriminado)
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
    
    # 2. Egresos por sueldos
    sql_sueldos = "SELECT COALESCE(SUM(total_pagado), 0) as total_sueldos FROM pagos WHERE date(created_at) BETWEEN ? AND ?"
    sueldos = Database.execute_query(sql_sueldos, (fecha_inicio, fecha_fin), fetch_one=True)
    total_sueldos = sueldos['total_sueldos'] if sueldos else 0
    
    # 3. Egresos por compras a proveedores
    sql_compras = """
        SELECT COALESCE(SUM(m.cantidad * p.precio_compra), 0) as total_compras
        FROM movimientos_stock m
        JOIN productos p ON m.producto_id = p.id
        WHERE m.tipo = 'entrada' AND date(m.created_at) BETWEEN ? AND ?
    """
    compras = Database.execute_query(sql_compras, (fecha_inicio, fecha_fin), fetch_one=True)
    total_compras = compras['total_compras'] if compras else 0
    
    # 4. Gastos generales
    sql_gastos = """
        SELECT categoria, COALESCE(SUM(monto), 0) as total_gastos
        FROM gastos_generales
        WHERE date(fecha) BETWEEN ? AND ?
        GROUP BY categoria
    """
    gastos_categorias = Database.execute_query(sql_gastos, (fecha_inicio, fecha_fin), fetch_all=True)
    gastos_categorias = [dict(g) for g in gastos_categorias] if gastos_categorias else []
    
    total_gastos = sum(g['total_gastos'] for g in gastos_categorias)
    total_egresos = total_sueldos + total_compras + total_gastos
    
    balance = ingresos['total_bruto'] - total_egresos
    margen = (balance / ingresos['total_bruto'] * 100) if ingresos['total_bruto'] > 0 else 0
    
    return jsonify({
        "success": True,
        "data": {
            "periodo": {"inicio": fecha_inicio, "fin": fecha_fin},
            "ingresos": {
                "neto": ingresos['total_neto'],
                "iva": ingresos['total_iva'],
                "bruto": ingresos['total_bruto'],
                "cantidad_ventas": ingresos['cantidad_ventas'],
                "ticket_promedio": round(ingresos['ticket_promedio'], 2)
            },
            "egresos": {
                "sueldos": total_sueldos,
                "compras_proveedores": total_compras,
                "gastos_generales": total_gastos,
                "total": total_egresos,
                "detalle_gastos": gastos_categorias
            },
            "balance": balance,
            "margen_ganancia": round(margen, 2)
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
    # CONVERSIÓN CRÍTICA PARA EVITAR EL ERROR JSON
    gastos_dict = [dict(g) for g in gastos] if gastos else []
    
    return jsonify({"success": True, "data": gastos_dict}), 200

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