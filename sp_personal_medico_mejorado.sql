-- ===============================================
-- STORED PROCEDURE PARA PERSONAL MÉDICO CON VISTA PARTICIONADA
-- Maneja Vista_INF_Personal con transacción distribuida
-- Contratos se maneja por separado desde Python
-- ===============================================

CREATE PROCEDURE SP_Create_PersonalMedico
    @ID_Hospital INT,
    @ID_Personal INT,
    @ID_Especialidad INT,
    @Nombre VARCHAR(50),
    @Apellido VARCHAR(50),
    @Teléfono VARCHAR(20)
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que no exista el personal médico
        IF EXISTS (SELECT 1 FROM Vista_INF_Personal WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal)
        BEGIN
            RAISERROR('Ya existe un personal médico con Hospital %d y Personal %d', 16, 1, @ID_Hospital, @ID_Personal);
            RETURN;
        END
        
        -- 2. Insertar en Vista_INF_Personal (particionada entre servidores)
        INSERT INTO Vista_INF_Personal (
            ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono
        )
        VALUES (
            @ID_Hospital, @ID_Personal, @ID_Especialidad, @Nombre, @Apellido, @Teléfono
        );
        
        COMMIT TRANSACTION;
        
        SELECT 'Personal médico creado exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Create_PersonalMedico: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ELIMINAR PERSONAL MÉDICO
-- ===============================================

CREATE PROCEDURE SP_Delete_PersonalMedico
    @ID_Hospital INT,
    @ID_Personal INT
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe el personal médico
        IF NOT EXISTS (SELECT 1 FROM Vista_INF_Personal WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal)
        BEGIN
            RAISERROR('No existe personal médico con Hospital %d y Personal %d', 16, 1, @ID_Hospital, @ID_Personal);
            RETURN;
        END
        
        -- 2. Eliminar de Vista_INF_Personal (particionada entre servidores)
        DELETE FROM Vista_INF_Personal 
        WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal;
        
        COMMIT TRANSACTION;
        
        SELECT 'Personal médico eliminado exitosamente de vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Delete_PersonalMedico: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ACTUALIZAR PERSONAL MÉDICO
-- ===============================================

CREATE PROCEDURE SP_Update_PersonalMedico
    @ID_Hospital INT,
    @ID_Personal INT,
    @ID_Especialidad INT,
    @Nombre VARCHAR(50),
    @Apellido VARCHAR(50),
    @Teléfono VARCHAR(20)
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe el personal médico
        IF NOT EXISTS (SELECT 1 FROM Vista_INF_Personal WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal)
        BEGIN
            RAISERROR('No existe personal médico con Hospital %d y Personal %d', 16, 1, @ID_Hospital, @ID_Personal);
            RETURN;
        END
        
        -- 2. Actualizar en Vista_INF_Personal (particionada entre servidores)
        UPDATE Vista_INF_Personal 
        SET ID_Especialidad = @ID_Especialidad,
            Nombre = @Nombre,
            Apellido = @Apellido,
            Teléfono = @Teléfono
        WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal;
        
        COMMIT TRANSACTION;
        
        SELECT 'Personal médico actualizado exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Update_PersonalMedico: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- VERSIÓN ALTERNATIVA: DISTRIBUTED TRANSACTION
-- (Solo si tienes múltiples servidores SQL Server)
-- ===============================================

/*
CREATE PROCEDURE SP_Create_PersonalMedico_Distributed
    @ID_Hospital INT,
    @ID_Personal INT,
    @ID_Especialidad INT,
    @Nombre VARCHAR(50),
    @Apellido VARCHAR(50),
    @Teléfono VARCHAR(20),
    @Salario DECIMAL(10, 2),
    @Fecha_Contrato DATE = NULL
AS
BEGIN
    SET XACT_ABORT ON;
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- Validaciones y operaciones...
        INSERT INTO Vista_INF_Personal (...);
        INSERT INTO Contratos (...);
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
*/

-- ===============================================
-- SCRIPT DE PRUEBA
-- ===============================================

-- Probar el SP
/*
EXEC SP_Create_PersonalMedico 
    @ID_Hospital = 1,
    @ID_Personal = 999,
    @ID_Especialidad = 1,
    @Nombre = 'Test',
    @Apellido = 'Usuario',
    @Teléfono = '123456789',
    @Salario = 2800.00,
    @Fecha_Contrato = '2025-07-30';

-- Verificar que se creó en ambas tablas
SELECT 'Vista_INF_Personal' as Tabla, * FROM Vista_INF_Personal WHERE ID_Hospital = 1 AND ID_Personal = 999;
SELECT 'Contratos' as Tabla, * FROM Contratos WHERE ID_Hospital = 1 AND ID_Personal = 999;

-- Limpiar datos de prueba
DELETE FROM Contratos WHERE ID_Hospital = 1 AND ID_Personal = 999;
DELETE FROM Vista_INF_Personal WHERE ID_Hospital = 1 AND ID_Personal = 999;
*/
