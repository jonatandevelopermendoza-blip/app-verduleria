-- Tabla de horarios asignados a empleados
CREATE TABLE IF NOT EXISTS horarios_empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    dia_semana TEXT NOT NULL CHECK (dia_semana IN ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo')),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    horas_esperadas DECIMAL(5,2) NOT NULL,
    activo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(persona_id, dia_semana),
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
);

-- Tabla de límites de horas
CREATE TABLE IF NOT EXISTS limites_horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('semanal', 'mensual')),
    limite_horas DECIMAL(6,2) NOT NULL,
    activo INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
);

-- Tabla de registros de pago
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    periodo TEXT NOT NULL,  -- '2025-01', '2025-02'
    horas_trabajadas DECIMAL(6,2) NOT NULL,
    horas_esperadas DECIMAL(6,2) NOT NULL,
    horas_extra DECIMAL(6,2) DEFAULT 0,
    sueldo_base DECIMAL(10,2) NOT NULL,
    pago_extra DECIMAL(10,2) DEFAULT 0,
    total_pagado DECIMAL(10,2) NOT NULL,
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'pagado', 'cancelado')),
    fecha_pago DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
);

-- Índices
CREATE INDEX idx_horarios_persona ON horarios_empleados(persona_id);
CREATE INDEX idx_limites_persona ON limites_horarios(persona_id);
CREATE INDEX idx_pagos_periodo ON pagos(periodo);