-- ===============================================
-- SCRIPT DE PRUEBA PARA STORED PROCEDURES DE CONTRATOS
-- CrearContrato, ActualizarContrato, EliminarContrato
-- ===============================================

-- 1. Ver registros existentes antes de la prueba
SELECT 'ANTES DE TODAS LAS PRUEBAS' as Estado, * FROM Contratos ORDER BY ID_Hospital, ID_Personal;

-- ===============================================
-- PRUEBA 1: CREAR CONTRATO SIN FECHA
-- ===============================================
PRINT 'PRUEBA 1: Creando contrato sin fecha';
EXEC CrearContrato @ID_Hospital = 1, @ID_Personal = 9999, @Salario = 2500.00;

-- Verificar que se insertó
SELECT 'DESPUÉS DE CREAR SIN FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 1 AND ID_Personal = 9999;

-- ===============================================
-- PRUEBA 2: CREAR CONTRATO CON FECHA
-- ===============================================
PRINT 'PRUEBA 2: Creando contrato con fecha';
EXEC CrearContrato @ID_Hospital = 2, @ID_Personal = 9998, @Salario = 3000.00, @Fecha_Contrato = '2025-07-30';

-- Verificar que se insertó
SELECT 'DESPUÉS DE CREAR CON FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 2 AND ID_Personal = 9998;

-- ===============================================
-- PRUEBA 3: ACTUALIZAR CONTRATO SIN FECHA
-- ===============================================
PRINT 'PRUEBA 3: Actualizando contrato sin modificar fecha';
EXEC ActualizarContrato @ID_Hospital = 1, @ID_Personal = 9999, @Salario = 2800.00;

-- Verificar actualización
SELECT 'DESPUÉS DE ACTUALIZAR SIN FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 1 AND ID_Personal = 9999;

-- ===============================================
-- PRUEBA 4: ACTUALIZAR CONTRATO CON FECHA
-- ===============================================
PRINT 'PRUEBA 4: Actualizando contrato con nueva fecha';
EXEC ActualizarContrato @ID_Hospital = 2, @ID_Personal = 9998, @Salario = 3500.00, @Fecha_Contrato = '2025-08-01';

-- Verificar actualización
SELECT 'DESPUÉS DE ACTUALIZAR CON FECHA' as Estado, * FROM Contratos WHERE ID_Hospital = 2 AND ID_Personal = 9998;

-- ===============================================
-- PRUEBA 5: ELIMINAR CONTRATOS
-- ===============================================
PRINT 'PRUEBA 5: Eliminando contratos de prueba';
EXEC EliminarContrato @ID_Hospital = 1, @ID_Personal = 9999;
EXEC EliminarContrato @ID_Hospital = 2, @ID_Personal = 9998;

-- Verificar eliminación
SELECT 'DESPUÉS DE ELIMINAR' as Estado, COUNT(*) as Contratos_Prueba_Restantes 
FROM Contratos WHERE ID_Personal IN (9999, 9998);

-- Ver todos los registros después de las pruebas
SELECT 'DESPUÉS DE TODAS LAS PRUEBAS' as Estado, * FROM Contratos ORDER BY ID_Hospital, ID_Personal;

-- ===============================================
-- PRUEBAS CON SINTAXIS CALL (alternativa)
-- ===============================================
PRINT 'PROBANDO SINTAXIS CALL:';

-- Si EXEC no funciona, probar con sintaxis CALL:
-- {CALL CrearContrato(1, 9997, 2750.00, NULL)}
-- {CALL ActualizarContrato(1, 9997, 3000.00, '2025-07-30')}
-- {CALL EliminarContrato(1, 9997)}

-- ===============================================
-- VERIFICACIONES ADICIONALES
-- ===============================================

-- Ver definición de los SPs
SELECT 
    ROUTINE_NAME,
    ROUTINE_TYPE,
    CREATED,
    LAST_ALTERED
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_NAME IN ('CrearContrato', 'ActualizarContrato', 'EliminarContrato')
ORDER BY ROUTINE_NAME;

-- Ver parámetros de los SPs
SELECT 
    SPECIFIC_NAME,
    PARAMETER_NAME,
    DATA_TYPE,
    PARAMETER_MODE,
    IS_RESULT
FROM INFORMATION_SCHEMA.PARAMETERS 
WHERE SPECIFIC_NAME IN ('CrearContrato', 'ActualizarContrato', 'EliminarContrato')
ORDER BY SPECIFIC_NAME, ORDINAL_POSITION;

PRINT 'FIN DE TODAS LAS PRUEBAS';
