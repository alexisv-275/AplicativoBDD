import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConnection:
    """Clase base para manejar conexiones y operaciones comunes"""
    
    def __init__(self):
        # Configuración para el nodo de Quito
        self.quito_config = {
            'server': os.getenv('DB_QUITO_SERVER'),
            'database': os.getenv('DB_QUITO_DATABASE'),
            'username': os.getenv('DB_QUITO_USERNAME'),
            'password': os.getenv('DB_QUITO_PASSWORD')
        }
        
        # Configuración para el nodo de Guayaquil
        self.guayaquil_config = {
            'server': os.getenv('DB_GUAYAQUIL_SERVER'),
            'database': os.getenv('DB_GUAYAQUIL_DATABASE'),
            'username': os.getenv('DB_GUAYAQUIL_USERNAME'),
            'password': os.getenv('DB_GUAYAQUIL_PASSWORD')
        }
    
    def detect_current_node(self):
        """Detecta el nodo actual probando conexiones"""
        # Intentar conectar a Quito primero
        if self._test_connection('quito'):
            return 'quito'
        elif self._test_connection('guayaquil'):
            return 'guayaquil'
        else:
            return None
    
    def _test_connection(self, node):
        """Prueba la conexión a un nodo específico"""
        try:
            connection = self.get_connection(node)
            if connection:
                connection.close()
                return True
        except:
            pass
        return False
    
    def get_connection_string(self, node='quito'):
        """Construye la cadena de conexión para SQL Server"""
        config = self.quito_config if node == 'quito' else self.guayaquil_config
        
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
            f"TrustServerCertificate=yes;"
        )
        return connection_string
    
    def get_connection(self, node=None):
        """Obtiene una conexión a la base de datos"""
        if node is None:
            node = self.detect_current_node()
            if node is None:
                raise Exception("No se puede conectar a ningún nodo")
        
        try:
            connection_string = self.get_connection_string(node)
            connection = pyodbc.connect(connection_string)
            return connection
        except pyodbc.Error as e:
            print(f"Error conectando a la base de datos {node}: {e}")
            return None
    
    def execute_query(self, query, params=None, node=None):
        """Ejecuta una consulta en el nodo especificado"""
        connection = self.get_connection(node)
        if not connection:
            return None
            
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Si es una consulta SELECT, retorna los resultados
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                # Para INSERT, UPDATE, DELETE
                connection.commit()
                return cursor.rowcount
                
        except pyodbc.Error as e:
            print(f"Error ejecutando consulta en {node}: {e}")
            connection.rollback()
            return None
        finally:
            connection.close()
