-- ============================================
-- BASE DE DATOS: verduleria.db (SQLite)
-- TABLAS: personas, usuarios, asistencias
-- ============================================

-- ============================================
-- TABLA: personas
-- ============================================
CREATE TABLE IF NOT EXISTS personas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    dni TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('admin', 'supervisor', 'empleado')),
    activo INTEGER DEFAULT 1,
    primer_login INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    ultimo_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE CASCADE
);

-- ============================================
-- TABLA: asistencias
-- ============================================
CREATE TABLE IF NOT EXISTS asistencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME,
    estado TEXT DEFAULT 'presente' CHECK (estado IN ('presente', 'ausente', 'justificado')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(persona_id, fecha),
    FOREIGN KEY (persona_id) REFERENCES personas(id) ON DELETE RESTRICT
);

-- ============================================
-- ÍNDICES
-- ============================================
CREATE INDEX IF NOT EXISTS idx_personas_email ON personas(email);
CREATE INDEX IF NOT EXISTS idx_personas_activo ON personas(activo);
CREATE INDEX IF NOT EXISTS idx_asistencias_fecha ON asistencias(fecha);
CREATE INDEX IF NOT EXISTS idx_asistencias_persona_fecha ON asistencias(persona_id, fecha);

-- ============================================
-- TRIGGER para actualizar updated_at
-- ============================================
CREATE TRIGGER IF NOT EXISTS update_personas_updated_at 
AFTER UPDATE ON personas
BEGIN
    UPDATE personas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_usuarios_updated_at 
AFTER UPDATE ON usuarios
BEGIN
    UPDATE usuarios SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_asistencias_updated_at 
AFTER UPDATE ON asistencias
BEGIN
    UPDATE asistencias SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;