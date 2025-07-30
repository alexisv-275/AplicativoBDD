-- ===============================================
-- SCRIPT DE PRUEBA PARA STORED PROCEDURE CrearContrato
-- ===============================================

-- 1. Ver registros existentes antes de la prueba
SELECT 'ANTES DE INSERCIÓN' as Estado, * FROM Contratos ORDER BY ID_Hospital, ID_Personal;

-- 2. Probar inserción sin fecha
EXEC CrearContrato @ID_Hospital = 1, @ID_Personal = 9999, @Salario = 2500.00;

-- 3. Verificar que se insertó
SELECT 'DESPUÉS DE INSERCIÓN SIN FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 1 AND ID_Personal = 9999;

-- 4. Probar inserción con fecha
EXEC CrearContrato @ID_Hospital = 2, @ID_Personal = 9998, @Salario = 3000.00, @Fecha_Contrato = '2025-07-30';

-- 5. Verificar que se insertó
SELECT 'DESPUÉS DE INSERCIÓN CON FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 2 AND ID_Personal = 9998;

-- 6. Ver todos los registros después de las inserciones
SELECT 'TODOS LOS REGISTROS DESPUÉS' as Estado, * FROM Contratos ORDER BY ID_Hospital, ID_Personal;

-- 7. Limpiar datos de prueba
DELETE FROM Contratos WHERE ID_Personal IN (9999, 9998);

-- 8. Verificar limpieza
SELECT 'DESPUÉS DE LIMPIEZA' as Estado, COUNT(*) as Total_Contratos FROM Contratos;

-- ===============================================
-- SCRIPT ALTERNATIVO: Probar con CALL en lugar de EXEC
-- ===============================================

-- Si EXEC no funciona, probar con sintaxis CALL:
-- {CALL CrearContrato(1, 9997, 2750.00, NULL)}
-- {CALL CrearContrato(2, 9996, 3250.00, '2025-07-30')}

-- ===============================================
-- VERIFICAR SI EL SP ESTÁ CREADO CORRECTAMENTE
-- ===============================================

-- Ver definición del SP
SELECT 
    ROUTINE_NAME,
    ROUTINE_TYPE,
    CREATED,
    LAST_ALTERED
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_NAME = 'CrearContrato';

-- Ver parámetros del SP
SELECT 
    PARAMETER_NAME,
    DATA_TYPE,
    PARAMETER_MODE,
    IS_RESULT
FROM INFORMATION_SCHEMA.PARAMETERS 
WHERE SPECIFIC_NAME = 'CrearContrato'
ORDER BY ORDINAL_POSITION;

-- ===============================================
-- VERIFICAR ESTRUCTURA DE LA TABLA
-- ===============================================

-- Ver estructura de la tabla Contratos
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'Contratos'
ORDER BY ORDINAL_POSITION;
