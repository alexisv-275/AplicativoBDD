-- ===============================================
-- STORED PROCEDURES PARA EXPERIENCIA CON VISTA PARTICIONADA
-- Maneja Vista_Experiencia con transacción distribuida
-- Rangos ID_Personal: Quito (1-10), Guayaquil (11-20)
-- ===============================================

-- ===============================================
-- STORED PROCEDURE PARA CREAR EXPERIENCIA
-- ===============================================

CREATE PROCEDURE SP_Create_Experiencia
    @ID_Hospital INT,
    @ID_Personal INT,
    @Cargo VARCHAR(50),
    @Años_exp INT
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que no exista la experiencia para ese personal y cargo
        IF EXISTS (
            SELECT 1 FROM Vista_Experiencia 
            WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal AND Cargo = @Cargo
        )
        BEGIN
            RAISERROR('Ya existe una experiencia con Hospital %d, Personal %d y Cargo %s', 16, 1, @ID_Hospital, @ID_Personal, @Cargo);
            RETURN;
        END
        
        -- 2. Insertar en Vista_Experiencia (particionada entre servidores)
        -- Nota: Los rangos de ID_Personal se manejan en el código Python, no en el SP
        INSERT INTO Vista_Experiencia (
            ID_Hospital, ID_Personal, Cargo, Años_exp
        )
        VALUES (
            @ID_Hospital, @ID_Personal, @Cargo, @Años_exp
        );
        
        COMMIT TRANSACTION;
        
        SELECT 'Experiencia creada exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Create_Experiencia: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ACTUALIZAR EXPERIENCIA
-- ===============================================

CREATE PROCEDURE SP_Update_Experiencia
    @ID_Hospital INT,
    @ID_Personal INT,
    @Cargo VARCHAR(50),
    @Años_exp INT
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe la experiencia
        IF NOT EXISTS (
            SELECT 1 FROM Vista_Experiencia 
            WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal AND Cargo = @Cargo
        )
        BEGIN
            RAISERROR('No existe experiencia con Hospital %d, Personal %d y Cargo %s', 16, 1, @ID_Hospital, @ID_Personal, @Cargo);
            RETURN;
        END
        
        -- 2. Actualizar en Vista_Experiencia (particionada entre servidores)
        UPDATE Vista_Experiencia
        SET Años_exp = @Años_exp
        WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal AND Cargo = @Cargo;
        
        COMMIT TRANSACTION;
        
        SELECT 'Experiencia actualizada exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Update_Experiencia: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ELIMINAR EXPERIENCIA
-- ===============================================

CREATE PROCEDURE SP_Delete_Experiencia
    @ID_Hospital INT,
    @ID_Personal INT,
    @Cargo VARCHAR(50)
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe la experiencia
        IF NOT EXISTS (
            SELECT 1 FROM Vista_Experiencia 
            WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal AND Cargo = @Cargo
        )
        BEGIN
            RAISERROR('No existe experiencia con Hospital %d, Personal %d y Cargo %s', 16, 1, @ID_Hospital, @ID_Personal, @Cargo);
            RETURN;
        END
        
        -- 2. Eliminar de Vista_Experiencia (particionada entre servidores)
        DELETE FROM Vista_Experiencia
        WHERE ID_Hospital = @ID_Hospital AND ID_Personal = @ID_Personal AND Cargo = @Cargo;
        
        COMMIT TRANSACTION;
        
        SELECT 'Experiencia eliminada exitosamente de vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Delete_Experiencia: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- SCRIPT DE PRUEBA
-- ===============================================

-- Probar el SP (Quito - rango ID_Personal 1-10)
/*
EXEC SP_Create_Experiencia 
    @ID_Hospital = 1,
    @ID_Personal = 2,
    @Cargo = 'Cardiólogo',
    @Años_exp = 5;

-- Verificar que se creó
SELECT * FROM Vista_Experiencia WHERE ID_Hospital = 1 AND ID_Personal = 2 AND Cargo = 'Cardiólogo';

-- Actualizar
EXEC SP_Update_Experiencia
    @ID_Hospital = 1,
    @ID_Personal = 2,
    @Cargo = 'Cardiólogo',
    @Años_exp = 6;

-- Limpiar datos de prueba
EXEC SP_Delete_Experiencia
    @ID_Hospital = 1,
    @ID_Personal = 2,
    @Cargo = 'Cardiólogo';
*/

-- Probar el SP (Guayaquil - rango ID_Personal 11-20)
/*
EXEC SP_Create_Experiencia 
    @ID_Hospital = 2,
    @ID_Personal = 12,
    @Cargo = 'Neurólogo',
    @Años_exp = 8;

-- Verificar que se creó
SELECT * FROM Vista_Experiencia WHERE ID_Hospital = 2 AND ID_Personal = 12 AND Cargo = 'Neurólogo';

-- Limpiar datos de prueba
EXEC SP_Delete_Experiencia
    @ID_Hospital = 2,
    @ID_Personal = 12,
    @Cargo = 'Neurólogo';
*/
