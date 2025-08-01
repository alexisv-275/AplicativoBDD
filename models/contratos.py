from .base import DatabaseConnection
import pyodbc

class ContratosManager(DatabaseConnection):
    def __init__(self):
        super().__init__()

    def get_contratos_table_name(self):
        """Obtener el nombre de la tabla Contratos según el nodo actual"""
        try:
            current_node = self.detect_current_node()
            if current_node == 'quito':
                # Acceso directo en Quito
                return "Contratos"
            else:
                # Linked server desde Guayaquil a Quito
                return "[ASUSVIVOBOOK].[Red_de_salud_Quito].[dbo].[Contratos]"
        except Exception as e:
            print(f"Error detectando nodo para contratos: {e}")
            # Default: asumir acceso directo
            return "Contratos"

    def get_all_contratos(self):
        """Obtener todos los contratos de la tabla Contratos (acceso local únicamente)"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT ID_Hospital, ID_Personal, Salario, Fecha_Contrato
            FROM Contratos
            ORDER BY ID_Hospital, ID_Personal
            """
            
            cursor.execute(query)
            contratos = []
            
            for row in cursor.fetchall():
                contrato = {
                    'ID_Hospital': row.ID_Hospital,
                    'ID_Personal': row.ID_Personal,
                    'Salario': row.Salario,
                    'Fecha_Contrato': row.Fecha_Contrato
                }
                contratos.append(contrato)
            
            cursor.close()
            connection.close()
            return contratos
            
        except Exception as e:
            print(f"Error al obtener contratos: {e}")
            return []

    def get_contrato_by_ids(self, id_hospital, id_personal):
        """Obtener un contrato específico por ID_Hospital e ID_Personal (usando linked server si es necesario)"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Obtener nombre de tabla según nodo
            tabla_contratos = self.get_contratos_table_name()
            
            query = f"""
            SELECT ID_Hospital, ID_Personal, Salario, Fecha_Contrato
            FROM {tabla_contratos}
            WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
            print(f"🔗 DEBUG: Buscando contrato en {tabla_contratos} para H={id_hospital}, P={id_personal}")
            cursor.execute(query, (id_hospital, id_personal))
            row = cursor.fetchone()
            
            contrato = None
            if row:
                contrato = {
                    'ID_Hospital': row.ID_Hospital,
                    'ID_Personal': row.ID_Personal,
                    'Salario': row.Salario,
                    'Fecha_Contrato': row.Fecha_Contrato
                }
            
            cursor.close()
            connection.close()
            return contrato
            
        except Exception as e:
            print(f"Error al obtener contrato por IDs: {e}")
            return None

    def create_contrato(self, id_hospital, id_personal, salario, fecha_contrato=None):
        """Crear un nuevo contrato usando Stored Procedure (usando linked server si es necesario)"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            # Determinar cómo ejecutar el SP según el nodo
            current_node = self.detect_current_node()
            if current_node == 'quito':
                # Ejecutar SP directamente en Quito
                sp_call = "{CALL CrearContrato (?, ?, ?, ?)}"
                print(f"🔗 DEBUG: Ejecutando SP local en Quito: {sp_call}")
            else:
                # Ejecutar SP remoto via linked server
                sp_call = "{CALL [ASUSVIVOBOOK].[Red_de_salud_Quito].[dbo].[CrearContrato] (?, ?, ?, ?)}"
                print(f"🔗 DEBUG: Ejecutando SP remoto via linked server: {sp_call}")
            
            cursor.execute(sp_call, (id_hospital, id_personal, salario, fecha_contrato))
            
            # Confirmar la transacción
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error al crear contrato: {e}")
            return False

    def update_contrato(self, id_hospital, id_personal, salario, fecha_contrato=None):
        """Actualizar un contrato existente usando Stored Procedure (acceso local únicamente)"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            sp_call = "{CALL ActualizarContrato (?, ?, ?, ?)}"
            cursor.execute(sp_call, (id_hospital, id_personal, salario, fecha_contrato))
            
            # Confirmar la transacción
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
                
        except Exception as e:
            print(f"Error al actualizar contrato: {e}")
            return False

    def delete_contrato(self, id_hospital, id_personal):
        """Eliminar un contrato usando Stored Procedure (usando linked server si es necesario)"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            # Determinar cómo ejecutar el SP según el nodo
            current_node = self.detect_current_node()
            if current_node == 'quito':
                # Ejecutar SP directamente en Quito
                sp_call = "{CALL EliminarContrato (?, ?)}"
                print(f"🔗 DEBUG: Ejecutando SP local en Quito: {sp_call}")
            else:
                # Ejecutar SP remoto via linked server
                sp_call = "{CALL [ASUSVIVOBOOK].[Red_de_salud_Quito].[dbo].[EliminarContrato] (?, ?)}"
                print(f"🔗 DEBUG: Ejecutando SP remoto via linked server: {sp_call}")
            
            cursor.execute(sp_call, (id_hospital, id_personal))
            
            # Confirmar la transacción
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
                
        except Exception as e:
            print(f"Error al eliminar contrato: {e}")
            return False

    def search_contratos(self, search_term):
        """Buscar contratos por término de búsqueda (acceso local únicamente)"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Buscar por ID_Hospital, ID_Personal o Salario
            query = """
            SELECT ID_Hospital, ID_Personal, Salario, Fecha_Contrato
            FROM Contratos
            WHERE CAST(ID_Hospital AS VARCHAR) LIKE ? 
               OR CAST(ID_Personal AS VARCHAR) LIKE ?
               OR CAST(Salario AS VARCHAR) LIKE ?
            ORDER BY ID_Hospital, ID_Personal
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            
            contratos = []
            for row in cursor.fetchall():
                contrato = {
                    'ID_Hospital': row.ID_Hospital,
                    'ID_Personal': row.ID_Personal,
                    'Salario': row.Salario,
                    'Fecha_Contrato': row.Fecha_Contrato
                }
                contratos.append(contrato)
            
            cursor.close()
            connection.close()
            return contratos
            
        except Exception as e:
            print(f"Error al buscar contratos: {e}")
            return []
