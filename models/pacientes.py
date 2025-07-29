from .base import DatabaseConnection

class PacientesModel(DatabaseConnection):
    """Modelo para manejar operaciones con Vista_Paciente"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_pacientes(self, node=None):
        """Obtiene todos los pacientes desde Vista_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'pacientes': [],
                    'node': None,
                    'total': 0
                }
            
            query = "SELECT * FROM Vista_Paciente ORDER BY ID_Hospital, ID_Paciente"
            results = self.execute_query(query, node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Vista_Paciente en nodo {current_node}',
                    'pacientes': [],
                    'node': current_node,
                    'total': 0
                }
            
            # Formatear fechas para el frontend
            for paciente in results:
                if paciente.get('FechaNacimiento'):
                    fecha = paciente['FechaNacimiento']
                    if hasattr(fecha, 'strftime'):
                        paciente['FechaNacimiento'] = fecha.strftime('%d/%m/%Y')
            
            return {
                'success': True,
                'pacientes': results,
                'node': current_node,
                'total': len(results),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pacientes': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_paciente_by_id(self, id_hospital, id_paciente, node=None):
        """Obtiene un paciente específico por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT * FROM Vista_Paciente 
                WHERE ID_Hospital = ? AND ID_Paciente = ?
            """
            results = self.execute_query(query, (id_hospital, id_paciente), node=current_node)
            
            if results and len(results) > 0:
                paciente = results[0]
                # Formatear fecha
                if paciente.get('FechaNacimiento'):
                    fecha = paciente['FechaNacimiento']
                    if hasattr(fecha, 'strftime'):
                        paciente['FechaNacimiento'] = fecha.strftime('%d/%m/%Y')
                return paciente
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo paciente: {e}")
            return None
    
    def create_paciente(self, paciente_data, node=None):
        """Crea un nuevo paciente en Vista_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # La vista debe manejar la inserción automáticamente según las restricciones
            query = """
                INSERT INTO Vista_Paciente 
                (ID_Hospital, ID_Paciente, Nombre, Apellido, Direccion, FechaNacimiento, Sexo, Telefono)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                paciente_data['ID_Hospital'],
                paciente_data['ID_Paciente'],
                paciente_data['Nombre'],
                paciente_data['Apellido'],
                paciente_data['Direccion'],
                paciente_data['FechaNacimiento'],
                paciente_data['Sexo'],
                paciente_data['Telefono']
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Paciente creado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar el paciente'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear paciente: {str(e)}'
            }
    
    def update_paciente(self, id_hospital, id_paciente, paciente_data, node=None):
        """Actualiza un paciente existente en Vista_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Vista_Paciente 
                SET Nombre = ?, Apellido = ?, Direccion = ?, 
                    FechaNacimiento = ?, Sexo = ?, Telefono = ?
                WHERE ID_Hospital = ? AND ID_Paciente = ?
            """
            
            params = (
                paciente_data['Nombre'],
                paciente_data['Apellido'],
                paciente_data['Direccion'],
                paciente_data['FechaNacimiento'],
                paciente_data['Sexo'],
                paciente_data['Telefono'],
                id_hospital,
                id_paciente
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Paciente actualizado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar el paciente (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar paciente: {str(e)}'
            }
    
    def delete_paciente(self, id_hospital, id_paciente, node=None):
        """Elimina un paciente de Vista_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Vista_Paciente 
                WHERE ID_Hospital = ? AND ID_Paciente = ?
            """
            
            result = self.execute_query(query, (id_hospital, id_paciente), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Paciente eliminado exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar el paciente (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar paciente: {str(e)}'
            }
    
    def search_pacientes(self, search_term, node=None):
        """Busca pacientes por nombre, apellido o ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'pacientes': []
                }
            
            query = """
                SELECT * FROM Vista_Paciente 
                WHERE Nombre LIKE ? OR Apellido LIKE ? OR 
                      CAST(ID_Paciente AS VARCHAR) LIKE ?
                ORDER BY ID_Hospital, ID_Paciente
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (search_pattern, search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'pacientes': []
                }
            
            # Formatear fechas
            for paciente in results:
                if paciente.get('FechaNacimiento'):
                    fecha = paciente['FechaNacimiento']
                    if hasattr(fecha, 'strftime'):
                        paciente['FechaNacimiento'] = fecha.strftime('%d/%m/%Y')
            
            return {
                'success': True,
                'pacientes': results,
                'node': current_node,
                'total': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pacientes': []
            }
