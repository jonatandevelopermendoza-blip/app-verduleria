from flask import request, jsonify
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido
from datetime import datetime

def registrar_venta():
    """POST /ventas - Registrar una nueva venta con IVA por producto"""
    data = request.get_json()
    
    if not data.get('productos') or len(data['productos']) == 0:
        return jsonify({"error": "Se requiere al menos un producto"}), 400
    
    conn = Database.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        subtotal_neto = 0.0
        iva_total = 0.0
        detalles = []
        
        for item in data['productos']:
            producto_id = item['producto_id']
            cantidad = item['cantidad']
            
            cursor.execute("""
                SELECT id, nombre, precio_venta, stock_actual, iva_porcentaje 
                FROM productos WHERE id = ?
            """, (producto_id,))
            producto = cursor.fetchone()
            
            if not producto:
                conn.rollback()
                return jsonify({"error": f"Producto ID {producto_id} no existe"}), 404
            
            # Convertir Row a dict
            producto = dict(producto)
            
            if producto['stock_actual'] < cantidad:
                conn.rollback()
                return jsonify({
                    "error": f"Stock insuficiente para {producto['nombre']}. "
                             f"Stock actual: {producto['stock_actual']}, solicitado: {cantidad}"
                }), 400
            
            iva_porcentaje = producto.get('iva_porcentaje', 21.0)
            precio_unitario = producto['precio_venta']
            subtotal_item = precio_unitario * cantidad
            iva_item = subtotal_item * (iva_porcentaje / 100)
            
            subtotal_neto += subtotal_item
            iva_total += iva_item
            
            detalles.append({
                'producto_id': producto_id,
                'producto_nombre': producto['nombre'],
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal_item,
                'iva_porcentaje': iva_porcentaje,
                'iva_monto': iva_item
            })
        
        total_bruto = subtotal_neto + iva_total
        
        # Generar número de factura
        from datetime import datetime
        fecha_str = datetime.now().strftime('%Y%m%d%H%M%S')
        numero_factura = f"F{len(data['productos'])}{fecha_str}"
        
        # Insertar cabecera de venta
        cursor.execute("""
            INSERT INTO ventas (numero_factura, persona_id, cliente_nombre, subtotal, iva, total, metodo_pago)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            numero_factura,
            request.persona_id,
            data.get('cliente_nombre', 'Consumidor Final'),
            subtotal_neto,
            iva_total,
            total_bruto,
            data.get('metodo_pago', 'efectivo')
        ))
        venta_id = cursor.lastrowid
        
        # Insertar detalles y actualizar stock
        for detalle in detalles:
            cursor.execute("""
                INSERT INTO ventas_detalle (venta_id, producto_id, cantidad, precio_unitario, subtotal, iva_porcentaje)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta_id, detalle['producto_id'], detalle['cantidad'],
                  detalle['precio_unitario'], detalle['subtotal'], detalle['iva_porcentaje']))
            
            cursor.execute("""
                UPDATE productos SET stock_actual = stock_actual - ? WHERE id = ?
            """, (detalle['cantidad'], detalle['producto_id']))
            
            cursor.execute("""
                INSERT INTO movimientos_stock (producto_id, tipo, cantidad, motivo, usuario_id)
                VALUES (?, 'venta', ?, ?, ?)
            """, (detalle['producto_id'], detalle['cantidad'],
                  f"Venta #{numero_factura}", request.persona_id))
        
        conn.commit()
        
        from src.utils.logger import log_action
        log_action('VENTA_REGISTRADA', user_id=request.persona_id,
                  details=f"Factura: {numero_factura} | Neto: ${subtotal_neto} | IVA: ${iva_total} | Total: ${total_bruto}")
        
        return jsonify({
            "success": True,
            "data": {
                "venta_id": venta_id,
                "numero_factura": numero_factura,
                "subtotal_neto": subtotal_neto,
                "iva_total": iva_total,
                "total_bruto": total_bruto,
                "productos": [{'nombre': d['producto_nombre'], 'cantidad': d['cantidad']} for d in detalles]
            }
        }), 201
        
    except Exception as e:
        conn.rollback()
        from src.utils.logger import log_error
        log_error("Error en registro de venta", user_id=request.persona_id, exception=e)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    
    finally:
        conn.close()
                
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