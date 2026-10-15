-- ============================================
-- MIGRACIÓN: Agregar IVA a productos
-- Fecha: 2026-08-02
-- ============================================

-- 1. Agregar columna iva_porcentaje a productos
ALTER TABLE productos ADD COLUMN iva_porcentaje DECIMAL(5,2) DEFAULT 21.0;

-- 2. Actualizar productos existentes con IVA por defecto
UPDATE productos SET iva_porcentaje = 21.0 WHERE iva_porcentaje IS NULL;

-- 3. Verificar
SELECT id, nombre, iva_porcentaje FROM productos LIMIT 5;