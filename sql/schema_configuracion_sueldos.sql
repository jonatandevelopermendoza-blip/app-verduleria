CREATE TABLE IF NOT EXISTS configuracion_sueldos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    sueldo_base DECIMAL(10,2) NOT NULL,
    valor_hora_extra DECIMAL(10,2) DEFAULT 15.0,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
);

-- Insertar configuración para empleados existentes
INSERT OR IGNORE INTO configuracion_sueldos (persona_id, sueldo_base, valor_hora_extra)
SELECT id, 1000.0, 15.0 FROM personas WHERE activo = 1;

-- Verificar
SELECT * FROM configuracion_sueldos;