-- ===============================================
-- STORED PROCEDURES PARA PACIENTES CON VISTA PARTICIONADA
-- Maneja Vista_Paciente con transacción distribuida
-- Rangos ID: Quito (1-20), Guayaquil (21-40)
-- ===============================================

-- ===============================================
-- STORED PROCEDURE PARA CREAR PACIENTE
-- ===============================================

CREATE PROCEDURE SP_Create_Paciente
    @ID_Hospital INT,
    @ID_Paciente INT,
    @Nombre VARCHAR(50),
    @Apellido VARCHAR(50),
    @Direccion VARCHAR(100),
    @FechaNacimiento DATE,
    @Sexo CHAR(1),
    @Telefono VARCHAR(20)
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que no exista el paciente
        IF EXISTS (SELECT 1 FROM Vista_Paciente WHERE ID_Hospital = @ID_Hospital AND ID_Paciente = @ID_Paciente)
        BEGIN
            RAISERROR('Ya existe un paciente con Hospital %d y Paciente %d', 16, 1, @ID_Hospital, @ID_Paciente);
            RETURN;
        END
        
        -- 2. Insertar en Vista_Paciente (particionada entre servidores)
        -- Nota: Los rangos de ID se manejan en el código Python, no en el SP
        INSERT INTO Vista_Paciente (
            ID_Hospital, ID_Paciente, Nombre, Apellido, Dirección, FechaNacimiento, Sexo, Teléfono
        )
        VALUES (
            @ID_Hospital, @ID_Paciente, @Nombre, @Apellido, @Direccion, @FechaNacimiento, @Sexo, @Telefono
        );
        
        COMMIT TRANSACTION;
        
        SELECT 'Paciente creado exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Create_Paciente: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ACTUALIZAR PACIENTE
-- ===============================================

CREATE PROCEDURE SP_Update_Paciente
    @ID_Hospital INT,
    @ID_Paciente INT,
    @Nombre VARCHAR(50),
    @Apellido VARCHAR(50),
    @Direccion VARCHAR(100),
    @FechaNacimiento DATE,
    @Sexo CHAR(1),
    @Telefono VARCHAR(20)
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe el paciente
        IF NOT EXISTS (SELECT 1 FROM Vista_Paciente WHERE ID_Hospital = @ID_Hospital AND ID_Paciente = @ID_Paciente)
        BEGIN
            RAISERROR('No existe paciente con Hospital %d y Paciente %d', 16, 1, @ID_Hospital, @ID_Paciente);
            RETURN;
        END
        
        -- 2. Actualizar en Vista_Paciente (particionada entre servidores)
        UPDATE Vista_Paciente 
        SET Nombre = @Nombre,
            Apellido = @Apellido,
            Dirección = @Direccion,
            FechaNacimiento = @FechaNacimiento,
            Sexo = @Sexo,
            Teléfono = @Telefono
        WHERE ID_Hospital = @ID_Hospital AND ID_Paciente = @ID_Paciente;
        
        COMMIT TRANSACTION;
        
        SELECT 'Paciente actualizado exitosamente en vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Update_Paciente: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- STORED PROCEDURE PARA ELIMINAR PACIENTE
-- ===============================================

CREATE PROCEDURE SP_Delete_Paciente
    @ID_Hospital INT,
    @ID_Paciente INT
AS
BEGIN
    SET XACT_ABORT ON;
    
    -- Usar transacción distribuida para vista particionada actualizable
    BEGIN DISTRIBUTED TRANSACTION;
    
    BEGIN TRY
        -- 1. Validar que existe el paciente
        IF NOT EXISTS (SELECT 1 FROM Vista_Paciente WHERE ID_Hospital = @ID_Hospital AND ID_Paciente = @ID_Paciente)
        BEGIN
            RAISERROR('No existe paciente con Hospital %d y Paciente %d', 16, 1, @ID_Hospital, @ID_Paciente);
            RETURN;
        END
        
        -- 2. Eliminar de Vista_Paciente (particionada entre servidores)
        DELETE FROM Vista_Paciente 
        WHERE ID_Hospital = @ID_Hospital AND ID_Paciente = @ID_Paciente;
        
        COMMIT TRANSACTION;
        
        SELECT 'Paciente eliminado exitosamente de vista particionada' AS Resultado;
        
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        
        -- Re-lanzar el error con información detallada
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY();
        DECLARE @ErrorState INT = ERROR_STATE();
        
        RAISERROR('Error en SP_Delete_Paciente: %s', @ErrorSeverity, @ErrorState, @ErrorMessage);
    END CATCH
END;

-- ===============================================
-- SCRIPT DE PRUEBA
-- ===============================================

-- Probar el SP (Quito - rango 1-20)
/*
EXEC SP_Create_Paciente 
    @ID_Hospital = 1,
    @ID_Paciente = 15,
    @Nombre = 'Juan',
    @Apellido = 'Pérez',
    @Dirección = 'Av. Amazonas 123',
    @Fecha_Nacimiento = '1990-05-15',
    @Sexo = 'M',
    @Teléfono = '0991234567';

-- Verificar que se creó
SELECT * FROM Vista_Paciente WHERE ID_Hospital = 1 AND ID_Paciente = 15;

-- Limpiar datos de prueba
DELETE FROM Vista_Paciente WHERE ID_Hospital = 1 AND ID_Paciente = 15;
*/

-- Probar el SP (Guayaquil - rango 21-40)
/*
EXEC SP_Create_Paciente 
    @ID_Hospital = 2,
    @ID_Paciente = 25,
    @Nombre = 'María',
    @Apellido = 'González',
    @Dirección = 'Av. 9 de Octubre 456',
    @Fecha_Nacimiento = '1985-08-20',
    @Sexo = 'F',
    @Teléfono = '0987654321';

-- Verificar que se creó
SELECT * FROM Vista_Paciente WHERE ID_Hospital = 2 AND ID_Paciente = 25;

-- Limpiar datos de prueba
DELETE FROM Vista_Paciente WHERE ID_Hospital = 2 AND ID_Paciente = 25;
*/
