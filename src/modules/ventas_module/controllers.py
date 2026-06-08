from flask import request, jsonify
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido
from datetime import datetime

def registrar_venta():
    """POST /ventas - Registrar una nueva venta"""
    data = request.get_json()
    
    if not data.get('productos') or len(data['productos']) == 0:
        return jsonify({"error": "Se requiere al menos un producto"}), 400
    
    subtotal = 0
    detalles = []
    
    # Procesar productos y actualizar stock
    for item in data['productos']:
        producto_id = item['producto_id']
        cantidad = item['cantidad']
        
        # Obtener precio del producto
        sql_prod = "SELECT precio_venta, stock_actual FROM productos WHERE id = ?"
        producto = Database.execute_query(sql_prod, (producto_id,), fetch_one=True)
        
        if not producto:
            return jsonify({"error": f"Producto {producto_id} no existe"}), 404
        
        if producto['stock_actual'] < cantidad:
            return jsonify({"error": f"Stock insuficiente para producto ID {producto_id}"}), 400
        
        subtotal_item = producto['precio_venta'] * cantidad
        subtotal += subtotal_item
        
        detalles.append({
            'producto_id': producto_id,
            'cantidad': cantidad,
            'precio_unitario': producto['precio_venta'],
            'subtotal': subtotal_item
        })
    
    # Calcular IVA (21% por defecto) y total
    iva = subtotal * 0.21
    total = subtotal + iva
    
    # Generar número de factura
    from datetime import datetime
    fecha_str = datetime.now().strftime('%Y%m%d%H%M%S')
    numero_factura = f"F{len(detalles)}{fecha_str}"
    
    # Insertar cabecera de venta
    sql_venta = """
        INSERT INTO ventas (numero_factura, persona_id, cliente_nombre, subtotal, iva, total, metodo_pago)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    venta_id = Database.execute_query(sql_venta, (
        numero_factura, request.persona_id, data.get('cliente_nombre', 'Consumidor Final'),
        subtotal, iva, total, data.get('metodo_pago', 'efectivo')
    ))
    
    # Insertar detalles y actualizar stock
    for detalle in detalles:
        sql_detalle = """
            INSERT INTO ventas_detalle (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """
        Database.execute_query(sql_detalle, (venta_id, detalle['producto_id'], detalle['cantidad'],
                                             detalle['precio_unitario'], detalle['subtotal']))
        
        # Actualizar stock (salida por venta)
        sql_stock = "UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?"
        Database.execute_query(sql_stock, (detalle['cantidad'], detalle['producto_id']))
        
        # Registrar movimiento de stock
        sql_mov = """
            INSERT INTO movimientos_stock (producto_id, tipo, cantidad, motivo, usuario_id)
            VALUES (?, 'venta', ?, ?, ?)
        """
        Database.execute_query(sql_mov, (detalle['producto_id'], detalle['cantidad'],
                                        f"Venta #{numero_factura}", request.persona_id))
    
    return jsonify({
        "success": True,
        "data": {
            "venta_id": venta_id,
            "numero_factura": numero_factura,
            "total": total,
            "subtotal": subtotal,
            "iva": iva
        }
    }), 201

def listar_ventas():
    """GET /ventas - Listar ventas con filtros"""
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    empleado_id = request.args.get('empleado_id')
    
    sql = """
        SELECT v.*, p.nombre as empleado_nombre, p.apellido as empleado_apellido
        FROM ventas v
        JOIN personas p ON v.persona_id = p.id
        WHERE 1=1
    """
    params = []
    
    if fecha_desde:
        sql += " AND v.fecha >= ?"
        params.append(fecha_desde)
    if fecha_hasta:
        sql += " AND v.fecha <= ?"
        params.append(fecha_hasta)
    if empleado_id:
        sql += " AND v.persona_id = ?"
        params.append(empleado_id)
    
    sql += " ORDER BY v.fecha DESC"
    
    ventas = Database.execute_query(sql, params, fetch_all=True)
    return jsonify({"success": True, "data": ventas}), 200

def detalle_venta(venta_id):
    """GET /ventas/<id> - Obtener detalle de una venta"""
    sql_cabecera = """
        SELECT v.*, p.nombre as empleado_nombre, p.apellido as empleado_apellido
        FROM ventas v
        JOIN personas p ON v.persona_id = p.id
        WHERE v.id = ?
    """
    venta = Database.execute_query(sql_cabecera, (venta_id,), fetch_one=True)
    
    if not venta:
        return jsonify({"error": "Venta no encontrada"}), 404
    
    sql_detalle = """
        SELECT d.*, pr.nombre as producto_nombre
        FROM ventas_detalle d
        JOIN productos pr ON d.producto_id = pr.id
        WHERE d.venta_id = ?
    """
    detalles = Database.execute_query(sql_detalle, (venta_id,), fetch_all=True)
    
    return jsonify({
        "success": True,
        "data": {
            "venta": venta,
            "detalles": detalles
        }
    }), 200

def ventas_dia():
    """GET /ventas/reporte/dia - Resumen de ventas del día"""
    hoy = datetime.now().date().isoformat()
    
    sql = """
        SELECT 
            COUNT(*) as cantidad_ventas,
            SUM(total) as total_ventas,
            AVG(total) as promedio_venta
        FROM ventas
        WHERE DATE(fecha) = ?
    """
    resumen = Database.execute_query(sql, (hoy,), fetch_one=True)
    
    sql_top = """
        SELECT pr.nombre, SUM(d.cantidad) as cantidad_vendida
        FROM ventas_detalle d
        JOIN productos pr ON d.producto_id = pr.id
        JOIN ventas v ON d.venta_id = v.id
        WHERE DATE(v.fecha) = ?
        GROUP BY pr.id
        ORDER BY cantidad_vendida DESC
        LIMIT 5
    """
    top_productos = Database.execute_query(sql_top, (hoy,), fetch_all=True)
    
    return jsonify({
        "success": True,
        "data": {
            "fecha": hoy,
            "resumen": resumen,
            "top_productos": top_productos
        }
    }), 200