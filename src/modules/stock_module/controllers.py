from flask import request, jsonify
from src.core.database import Database
from src.middleware.auth import token_requerido, rol_requerido

# ========== CATEGORÍAS ==========
def listar_categorias():
    """GET /stock/categorias - Listar todas las categorías"""
    sql = "SELECT * FROM categorias WHERE activo = 1 ORDER BY nombre"
    categorias = Database.execute_query(sql, fetch_all=True)
    return jsonify({"success": True, "data": categorias}), 200

def crear_categoria():
    """POST /stock/categorias - Crear nueva categoría (admin)"""
    data = request.get_json()
    if not data.get('nombre'):
        return jsonify({"error": "Nombre requerido"}), 400
    
    sql = "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)"
    Database.execute_query(sql, (data['nombre'], data.get('descripcion', '')))
    return jsonify({"success": True, "message": "Categoría creada"}), 201

# ========== PRODUCTOS ==========
def listar_productos():
    """GET /stock/productos - Listar productos con filtros"""
    categoria_id = request.args.get('categoria_id')
    stock_bajo = request.args.get('stock_bajo')
    
    sql = """
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.activo = 1
    """
    params = []
    
    if categoria_id:
        sql += " AND p.categoria_id = ?"
        params.append(categoria_id)
    
    if stock_bajo:
        sql += " AND p.stock_actual <= p.stock_minimo"
    
    sql += " ORDER BY p.nombre"
    
    productos = Database.execute_query(sql, params, fetch_all=True)
    return jsonify({"success": True, "data": productos}), 200

def crear_producto():
    data = request.get_json()
    
    campos = ['nombre', 'precio_compra', 'precio_venta']
    for campo in campos:
        if campo not in data:
            return jsonify({"error": f"Falta campo requerido: {campo}"}), 400
    
    # Obtener IVA (por defecto 21%)
    iva_porcentaje = data.get('iva_porcentaje', 21.0)
    
    # Validar que el IVA existe en la tabla de tasas
    iva_valid = Database.execute_query(
        "SELECT id FROM tasas_iva WHERE porcentaje = ? AND activo = 1",
        (iva_porcentaje,), fetch_one=True
    )
    if not iva_valid:
        return jsonify({"error": f"Tasa de IVA {iva_porcentaje}% no válida"}), 400
    
    sql = """
        INSERT INTO productos (nombre, descripcion, categoria_id, precio_compra, precio_venta,
                              stock_actual, stock_minimo, unidad_medida, codigo_barras, iva_porcentaje)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        Database.execute_query(sql, (
            data['nombre'],
            data.get('descripcion', ''),
            data.get('categoria_id'),
            data['precio_compra'],
            data['precio_venta'],
            data.get('stock_actual', 0),
            data.get('stock_minimo', 0),
            data.get('unidad_medida', 'unidad'),
            data.get('codigo_barras'),
            iva_porcentaje
        ))
        return jsonify({"success": True, "message": "Producto creado correctamente"}), 201
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return jsonify({"error": "El código de barras ya existe"}), 400
        return jsonify({"error": str(e)}), 500
    
def actualizar_stock():
    """POST /stock/movimientos - Registrar movimiento de stock"""
    data = request.get_json()
    
    campos = ['producto_id', 'tipo', 'cantidad']
    for campo in campos:
        if campo not in data:
            return jsonify({"error": f"Falta campo: {campo}"}), 400
    
    if data['tipo'] not in ['entrada', 'salida', 'ajuste', 'venta']:
        return jsonify({"error": "Tipo inválido"}), 400
    
    # Actualizar stock del producto
    signo = 1 if data['tipo'] in ['entrada', 'ajuste_positivo'] else -1
    sql_stock = "UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?"
    Database.execute_query(sql_stock, (data['cantidad'] * signo, data['producto_id']))
    
    # Registrar movimiento
    sql_mov = """
        INSERT INTO movimientos_stock (producto_id, tipo, cantidad, motivo, usuario_id)
        VALUES (?, ?, ?, ?, ?)
    """
    Database.execute_query(sql_mov, (
        data['producto_id'], data['tipo'], data['cantidad'],
        data.get('motivo', ''), request.persona_id
    ))
    
    return jsonify({"success": True, "message": "Stock actualizado"}), 200

def stock_bajo():
    """GET /stock/alertas - Productos con stock bajo"""
    sql = """
        SELECT p.*, c.nombre as categoria_nombre
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.stock_actual <= p.stock_minimo AND p.activo = 1
        ORDER BY (p.stock_actual * 1.0 / p.stock_minimo) ASC
    """
    productos = Database.execute_query(sql, fetch_all=True)
    return jsonify({"success": True, "data": productos}), 200

def listar_tasas_iva():
    """GET /stock/tasas-iva - Listar tasas de IVA disponibles"""
    sql = "SELECT id, nombre, porcentaje FROM tasas_iva WHERE activo = 1 ORDER BY porcentaje"
    tasas = Database.execute_query(sql, fetch_all=True)
    return jsonify({"success": True, "data": tasas}), 200

def actualizar_producto(producto_id):
    data = request.get_json()
    
    # Verificar que el producto existe
    existe = Database.execute_query("SELECT id FROM productos WHERE id = ?", (producto_id,), fetch_one=True)
    if not existe:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    # Obtener IVA (por defecto 21%)
    iva_porcentaje = data.get('iva_porcentaje', 21.0)
    
    # Validar IVA
    iva_valid = Database.execute_query(
        "SELECT id FROM tasas_iva WHERE porcentaje = ? AND activo = 1",
        (iva_porcentaje,), fetch_one=True
    )
    if not iva_valid:
        return jsonify({"error": f"Tasa de IVA {iva_porcentaje}% no válida"}), 400
    
    sql = """
        UPDATE productos 
        SET nombre = ?, descripcion = ?, categoria_id = ?, 
            precio_compra = ?, precio_venta = ?, stock_minimo = ?,
            unidad_medida = ?, codigo_barras = ?, iva_porcentaje = ?
        WHERE id = ?
    """
    Database.execute_query(sql, (
        data.get('nombre'),
        data.get('descripcion', ''),
        data.get('categoria_id'),
        data.get('precio_compra'),
        data.get('precio_venta'),
        data.get('stock_minimo', 0),
        data.get('unidad_medida', 'unidad'),
        data.get('codigo_barras'),
        iva_porcentaje,
        producto_id
    ))
    return jsonify({"success": True, "message": "Producto actualizado"}), 200