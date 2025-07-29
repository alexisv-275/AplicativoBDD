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
    
    def detect_current_node(self):
        """Detecta a qué nodo está conectado actualmente el aplicativo"""
        # Primero intenta Quito
        try:
            connection = self.get_connection('quito')
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT @@SERVERNAME")
                server_name = cursor.fetchone()[0]
                connection.close()
                
                # Si es ASUSVIVOBOOK, es Quito
                if 'ASUSVIVOBOOK' in server_name.upper():
                    return 'quito'
        except:
            pass
        
        # Luego intenta Guayaquil
        try:
            connection = self.get_connection('guayaquil')
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT @@SERVERNAME")
                server_name = cursor.fetchone()[0]
                connection.close()
                
                # Si es DESKTOP-5U7KKBV, es Guayaquil
                if 'DESKTOP-5U7KKBV' in server_name.upper():
                    return 'guayaquil'
        except:
            pass
        
        # Por defecto, Quito (nodo principal)
        return 'quito'
    
    def get_vista_pacientes(self):
        """Obtiene todos los pacientes desde Vista_Paciente del nodo actual"""
        current_node = self.detect_current_node()
        
        query = """
        SELECT ID_Hospital, ID_Paciente, Nombre, Apellido, 
               Dirección, FechaNacimiento, Sexo, Teléfono
        FROM Vista_Paciente
        ORDER BY ID_Hospital, ID_Paciente
        """
        
        return self.execute_query(query, node=current_node)
    
    def insert_paciente(self, id_hospital, nombre, apellido, direccion, fecha_nac, sexo, telefono):
        """Inserta un nuevo paciente en Vista_Paciente"""
        current_node = self.detect_current_node()
        
        query = """
        INSERT INTO Vista_Paciente (ID_Hospital, Nombre, Apellido, Dirección, FechaNacimiento, Sexo, Teléfono)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (id_hospital, nombre, apellido, direccion, fecha_nac, sexo, telefono)
        return self.execute_query(query, params, current_node)
    
    def update_paciente(self, id_hospital, id_paciente, nombre, apellido, direccion, fecha_nac, sexo, telefono):
        """Actualiza un paciente en Vista_Paciente"""
        current_node = self.detect_current_node()
        
        query = """
        UPDATE Vista_Paciente 
        SET Nombre = ?, Apellido = ?, Dirección = ?, FechaNacimiento = ?, Sexo = ?, Teléfono = ?
        WHERE ID_Hospital = ? AND ID_Paciente = ?
        """
        
        params = (nombre, apellido, direccion, fecha_nac, sexo, telefono, id_hospital, id_paciente)
        return self.execute_query(query, params, current_node)
    
    def delete_paciente(self, id_hospital, id_paciente):
        """Elimina un paciente de Vista_Paciente"""
        current_node = self.detect_current_node()
        
        query = """
        DELETE FROM Vista_Paciente 
        WHERE ID_Hospital = ? AND ID_Paciente = ?
        """
        
        params = (id_hospital, id_paciente)
        return self.execute_query(query, params, current_node)
