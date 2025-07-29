import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
class DatabaseConnection:
    """Clase para manejar las conexiones a ambos nodos de la base de datos distribuida"""
    
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
    
    def get_connection(self, node='quito'):
        """Obtiene una conexión a la base de datos especificada"""
        try:
            connection_string = self.get_connection_string(node)
            connection = pyodbc.connect(connection_string)
            return connection
        except pyodbc.Error as e:
            print(f"Error conectando a la base de datos {node}: {e}")
            return None
    
    def execute_query(self, query, params=None, node='quito'):
        """Ejecuta una consulta en el nodo especificado"""
        connection = self.get_connection(node)
        if connection:
            try:
                cursor = connection.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Si es una consulta SELECT, retorna los resultados
                if query.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
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
        return None
    
    def execute_distributed_query(self, query, params=None):
        """Ejecuta la misma consulta en ambos nodos (para vistas distribuidas)"""
        results = {}
        
        # Ejecutar en Quito
        quito_result = self.execute_query(query, params, 'quito')
        results['quito'] = quito_result
        
        # Ejecutar en Guayaquil
        guayaquil_result = self.execute_query(query, params, 'guayaquil')
        results['guayaquil'] = guayaquil_result
        
        return results
