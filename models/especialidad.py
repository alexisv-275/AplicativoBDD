from .base import DatabaseConnection

class EspecialidadModel(DatabaseConnection):
    """Modelo para manejar operaciones con la tabla Especialidad"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_especialidades(self, node=None):
        """Obtiene todas las especialidades desde la tabla Especialidad"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'especialidades': [],
                    'node': None,
                    'total': 0
                }
            
            query = "SELECT ID_Especialidad, Área FROM Especialidad ORDER BY ID_Especialidad"
            results = self.execute_query(query, node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and len(results) > 0:
                print(f"Campos disponibles en Especialidad: {list(results[0].keys())}")
                print(f"Primer registro: {results[0]}")
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Especialidad en nodo {current_node}',
                    'especialidades': [],
                    'node': current_node,
                    'total': 0
                }
            
            return {
                'success': True,
                'especialidades': results,
                'node': current_node,
                'total': len(results),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'especialidades': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_especialidad_by_id(self, id_especialidad, node=None):
        """Obtiene una especialidad específica por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT ID_Especialidad, Área FROM Especialidad 
                WHERE ID_Especialidad = ?
            """
            results = self.execute_query(query, (id_especialidad,), node=current_node)
            
            if results and len(results) > 0:
                return results[0]
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo especialidad: {e}")
            return None
    
    def create_especialidad(self, especialidad_data, node=None):
        """Crea una nueva especialidad en la tabla Especialidad"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                INSERT INTO Especialidad (Área)
                VALUES (?)
            """
            
            params = (especialidad_data['Área'],)
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Especialidad creada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar la especialidad'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear especialidad: {str(e)}'
            }
    
    def update_especialidad(self, id_especialidad, especialidad_data, node=None):
        """Actualiza una especialidad existente en la tabla Especialidad"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Especialidad 
                SET Área = ?
                WHERE ID_Especialidad = ?
            """
            
            params = (
                especialidad_data['Área'],
                id_especialidad
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Especialidad actualizada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar la especialidad (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar especialidad: {str(e)}'
            }
    
    def delete_especialidad(self, id_especialidad, node=None):
        """Elimina una especialidad de la tabla Especialidad"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Especialidad 
                WHERE ID_Especialidad = ?
            """
            
            result = self.execute_query(query, (id_especialidad,), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Especialidad eliminada exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar la especialidad (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar especialidad: {str(e)}'
            }
    
    def search_especialidades(self, search_term, node=None):
        """Busca especialidades por área o ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'especialidades': []
                }
            
            query = """
                SELECT ID_Especialidad, Área FROM Especialidad 
                WHERE Área LIKE ? OR 
                      CAST(ID_Especialidad AS VARCHAR) LIKE ?
                ORDER BY ID_Especialidad
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'especialidades': []
                }
            
            return {
                'success': True,
                'especialidades': results,
                'node': current_node,
                'total': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'especialidades': []
            }
