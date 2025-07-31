-- ===============================================
-- STORED PROCEDURES PARA VISTA_ATENCION_MEDICA (PARTICIONADA ACTUALIZABLE)
-- Maneja Vista_Atencion_Medica con transacción distribuida
-- ===============================================

-- ===============================================
-- CREAR ATENCIÓN MÉDICA
-- ===============================================
CREATE PROCEDURE SP_Create_Atencion_Medica
    @ID_Hospital INT,
    @ID_Atención INT,
    @ID_Personal INT,
    @ID_Paciente INT,
    @ID_Tipo INT,
    @Fecha DATE,
    @Diagnostico VARCHAR(255),
    @Descripción VARCHAR(255),
    @Tratamiento VARCHAR(255)
AS
BEGIN
    SET XACT_ABORT ON;
    BEGIN DISTRIBUTED TRANSACTION;
    BEGIN TRY
        -- Validar que no exista la atención
        IF EXISTS (SELECT 1 FROM Vista_Atencion_Medica WHERE ID_Hospital = @ID_Hospital AND ID_Atención = @ID_Atención)
        BEGIN
            RAISERROR('Ya existe una atención con Hospital %d y Atención %d', 16, 1, @ID_Hospital, @ID_Atención);
            RETURN;
        END
        
        -- Insertar en Vista_Atencion_Medica
        INSERT INTO Vista_Atencion_Medica (
            ID_Hospital, ID_Atención, ID_Personal, ID_Paciente, ID_Tipo,
            Fecha, Diagnostico, Descripción, Tratamiento
        )
        VALUES (
            @ID_Hospital, @ID_Atención, @ID_Personal, @ID_Paciente, @ID_Tipo,
            @Fecha, @Diagnostico, @Descripción, @Tratamiento
        );
        
        COMMIT TRANSACTION;
        SELECT 'Atención médica creada exitosamente en vista particionada' AS Resultado;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        RAISERROR('Error en SP_Create_Atencion_Medica: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;
GO

-- ===============================================
-- ACTUALIZAR ATENCIÓN MÉDICA
-- ===============================================
CREATE PROCEDURE SP_Update_Atencion_Medica
    @ID_Hospital INT,
    @ID_Atención INT,
    @ID_Personal INT,
    @ID_Paciente INT,
    @ID_Tipo INT,
    @Fecha DATE,
    @Diagnostico VARCHAR(255),
    @Descripción VARCHAR(255),
    @Tratamiento VARCHAR(255)
AS
BEGIN
    SET XACT_ABORT ON;
    BEGIN DISTRIBUTED TRANSACTION;
    BEGIN TRY
        -- Validar que existe la atención
        IF NOT EXISTS (SELECT 1 FROM Vista_Atencion_Medica WHERE ID_Hospital = @ID_Hospital AND ID_Atención = @ID_Atención)
        BEGIN
            RAISERROR('No existe atención con Hospital %d y Atención %d', 16, 1, @ID_Hospital, @ID_Atención);
            RETURN;
        END
        
        -- Actualizar en Vista_Atencion_Medica
        UPDATE Vista_Atencion_Medica
        SET ID_Personal = @ID_Personal,
            ID_Paciente = @ID_Paciente,
            ID_Tipo = @ID_Tipo,
            Fecha = @Fecha,
            Diagnostico = @Diagnostico,
            Descripción = @Descripción,
            Tratamiento = @Tratamiento
        WHERE ID_Hospital = @ID_Hospital AND ID_Atención = @ID_Atención;
        
        COMMIT TRANSACTION;
        SELECT 'Atención médica actualizada exitosamente en vista particionada' AS Resultado;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        RAISERROR('Error en SP_Update_Atencion_Medica: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;
GO

-- ===============================================
-- ELIMINAR ATENCIÓN MÉDICA
-- ===============================================
CREATE PROCEDURE SP_Delete_Atencion_Medica
    @ID_Hospital INT,
    @ID_Atención INT
AS
BEGIN
    SET XACT_ABORT ON;
    BEGIN DISTRIBUTED TRANSACTION;
    BEGIN TRY
        -- Validar que existe la atención
        IF NOT EXISTS (SELECT 1 FROM Vista_Atencion_Medica WHERE ID_Hospital = @ID_Hospital AND ID_Atención = @ID_Atención)
        BEGIN
            RAISERROR('No existe atención con Hospital %d y Atención %d', 16, 1, @ID_Hospital, @ID_Atención);
            RETURN;
        END
        
        -- Eliminar de Vista_Atencion_Medica
        DELETE FROM Vista_Atencion_Medica
        WHERE ID_Hospital = @ID_Hospital AND ID_Atención = @ID_Atención;
        
        COMMIT TRANSACTION;
        SELECT 'Atención médica eliminada exitosamente de vista particionada' AS Resultado;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        RAISERROR('Error en SP_Delete_Atencion_Medica: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;
GO

-- ===============================================
-- SCRIPT DE PRUEBA
-- ===============================================
-- Probar el SP
/*
EXEC SP_Create_Atencion_Medica 
    @ID_Hospital = 1,
    @ID_Atención = 999,
    @ID_Personal = 1,
    @ID_Paciente = 1,
    @ID_Tipo = 1,
    @Fecha = '2025-07-31',
    @Diagnostico = 'Test Diagnóstico',
    @Descripción = 'Test Descripción',
    @Tratamiento = 'Test Tratamiento';

EXEC SP_Update_Atencion_Medica 
    @ID_Hospital = 1,
    @ID_Atención = 999,
    @ID_Personal = 2,
    @ID_Paciente = 2,
    @ID_Tipo = 2,
    @Fecha = '2025-08-01',
    @Diagnostico = 'Diagnóstico actualizado',
    @Descripción = 'Descripción actualizada',
    @Tratamiento = 'Tratamiento actualizado';

EXEC SP_Delete_Atencion_Medica 
    @ID_Hospital = 1,
    @ID_Atención = 999;

-- Limpiar datos de prueba
DELETE FROM Vista_Atencion_Medica WHERE ID_Hospital = 1 AND ID_Atención = 999;
*/
