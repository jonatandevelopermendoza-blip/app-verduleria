-- Gastos generales (luz, agua, alquiler, etc.)
CREATE TABLE IF NOT EXISTS gastos_generales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    concepto TEXT NOT NULL,
    descripcion TEXT,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    categoria TEXT DEFAULT 'operativo',
    comprobante TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_gastos_fecha ON gastos_generales(fecha);
CREATE INDEX IF NOT EXISTS idx_gastos_categoria ON gastos_generales(categoria);