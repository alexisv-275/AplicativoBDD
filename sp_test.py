def create_contrato_with_sp(self, id_hospital, id_personal, salario, fecha_contrato=None):
    """Crear contrato usando Stored Procedure con sintaxis corregida"""
    try:
        connection = self.get_connection()
        cursor = connection.cursor()

        if fecha_contrato:
            # Sintaxis corregida - solo parámetros posicionales
            cursor.execute("{CALL CrearContrato (?, ?, ?, ?)}", 
                         (id_hospital, id_personal, salario, fecha_contrato))
        else:
            # Para NULL, usar None explícitamente
            cursor.execute("{CALL CrearContrato (?, ?, ?, ?)}", 
                         (id_hospital, id_personal, salario, None))
        
        # NO hacer commit aquí - el SP ya maneja la transacción
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error al crear contrato con SP: {e}")
        return False
