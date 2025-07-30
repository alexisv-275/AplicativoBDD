from .base import DatabaseConnection
import pyodbc

class ContratosManager(DatabaseConnection):
    def __init__(self):
        super().__init__()

    def get_all_contratos(self):
        """Obtener todos los contratos de la tabla Contratos (sin filtrado por nodo)"""
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
        """Obtener un contrato específico por ID_Hospital e ID_Personal"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT ID_Hospital, ID_Personal, Salario, Fecha_Contrato
            FROM Contratos 
            WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
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
        """Crear un nuevo contrato usando Stored Procedure"""
        try:
            connection = self.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            # Ejecutar el Stored Procedure CrearContrato
            cursor.execute("{CALL CrearContrato (?, ?, ?, ?)}", 
                         (id_hospital, id_personal, salario, fecha_contrato))
            
            # Confirmar la transacción
            connection.commit()
            
            cursor.close()
            connection.close()
            return True
            
        except Exception as e:
            print(f"Error al crear contrato: {e}")
            return False

    def update_contrato(self, id_hospital, id_personal, salario, fecha_contrato=None):
        """Actualizar un contrato existente"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            if fecha_contrato:
                query = """
                UPDATE Contratos 
                SET Salario = ?, Fecha_Contrato = ?
                WHERE ID_Hospital = ? AND ID_Personal = ?
                """
                cursor.execute(query, (salario, fecha_contrato, id_hospital, id_personal))
            else:
                query = """
                UPDATE Contratos 
                SET Salario = ?
                WHERE ID_Hospital = ? AND ID_Personal = ?
                """
                cursor.execute(query, (salario, id_hospital, id_personal))
            
            if cursor.rowcount > 0:
                connection.commit()
                cursor.close()
                connection.close()
                return True
            else:
                cursor.close()
                connection.close()
                return False
                
        except Exception as e:
            print(f"Error al actualizar contrato: {e}")
            return False

    def delete_contrato(self, id_hospital, id_personal):
        """Eliminar un contrato"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query = "DELETE FROM Contratos WHERE ID_Hospital = ? AND ID_Personal = ?"
            cursor.execute(query, (id_hospital, id_personal))
            
            if cursor.rowcount > 0:
                connection.commit()
                cursor.close()
                connection.close()
                return True
            else:
                cursor.close()
                connection.close()
                return False
                
        except Exception as e:
            print(f"Error al eliminar contrato: {e}")
            return False

    def search_contratos(self, search_term):
        """Buscar contratos por término de búsqueda (sin filtrado por nodo)"""
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
