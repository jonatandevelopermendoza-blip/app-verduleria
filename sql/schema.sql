-- ============================================
-- BASE DE DATOS: verduleria_db
-- TABLAS: personas, usuarios
-- RELACIÓN: 1 a N (una persona → múltiples usuarios)
-- ============================================

USE verduleria_db;

-- ============================================
-- TABLA: personas
-- ============================================
CREATE TABLE IF NOT EXISTS personas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    rol ENUM('admin', 'supervisor', 'empleado') NOT NULL,
    activo BOOLEAN DEFAULT 1,
    primer_login BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: usuarios
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    ultimo_login TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_persona 
        FOREIGN KEY (persona_id) 
        REFERENCES personas(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================
-- ÍNDICES ADICIONALES
-- ============================================

CREATE INDEX idx_personas_email ON personas(email);
CREATE INDEX idx_personas_activo ON personas(activo);
CREATE INDEX idx_usuarios_ultimo_login ON usuarios(ultimo_login);
