-- ============================================
-- TABLA: tasas_iva (opciones configurables)
-- ============================================

CREATE TABLE IF NOT EXISTS tasas_iva (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL UNIQUE,
    activo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insertar tasas predeterminadas
INSERT OR IGNORE INTO tasas_iva (nombre, porcentaje) VALUES ('Exento', 0.0);
INSERT OR IGNORE INTO tasas_iva (nombre, porcentaje) VALUES ('Superreducido', 4.0);
INSERT OR IGNORE INTO tasas_iva (nombre, porcentaje) VALUES ('Reducido', 10.5);
INSERT OR IGNORE INTO tasas_iva (nombre, porcentaje) VALUES ('General', 21.0);

-- Verificar
SELECT * FROM tasas_iva;