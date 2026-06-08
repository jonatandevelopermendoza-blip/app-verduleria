-- Tabla de ventas (cabecera)
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_factura TEXT UNIQUE NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    persona_id INTEGER NOT NULL,  -- empleado que registra la venta
    cliente_nombre TEXT,
    subtotal DECIMAL(10,2) NOT NULL,
    iva DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    metodo_pago TEXT DEFAULT 'efectivo',
    estado TEXT DEFAULT 'completada',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

-- Tabla de detalles de venta
CREATE TABLE IF NOT EXISTS ventas_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- Índices
CREATE INDEX idx_ventas_fecha ON ventas(fecha);
CREATE INDEX idx_ventas_empleado ON ventas(persona_id);
CREATE INDEX idx_ventas_detalle_venta ON ventas_detalle(venta_id);