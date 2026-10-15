-- ============================================
-- MIGRACIÓN: Agregar IVA a ventas_detalle
-- Fecha: 2026-08-02
-- ============================================

-- 1. Agregar columna iva_porcentaje a ventas_detalle
ALTER TABLE ventas_detalle ADD COLUMN iva_porcentaje DECIMAL(5,2) DEFAULT 21.0;

-- 2. Verificar
SELECT id, venta_id, producto_id, iva_porcentaje FROM ventas_detalle LIMIT 5;