from .base import DatabaseConnection

class ExperienciaModel(DatabaseConnection):
    """Modelo para manejar operaciones con Vista_Experiencia"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_experiencias(self, node=None):
        """Obtiene todas las experiencias desde Vista_Experiencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'experiencias': [],
                    'node': None,
                    'total': 0
                }
            
            query = "SELECT * FROM Vista_Experiencia ORDER BY ID_Hospital, ID_Personal"
            results = self.execute_query(query, node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and len(results) > 0:
                print(f"Campos disponibles en Vista_Experiencia: {list(results[0].keys())}")
                print(f"Primer registro: {results[0]}")
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Vista_Experiencia en nodo {current_node}',
                    'experiencias': [],
                    'node': current_node,
                    'total': 0
                }
            
            return {
                'success': True,
                'experiencias': results,
                'node': current_node,
                'total': len(results),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'experiencias': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_experiencia_by_id(self, id_hospital, id_personal, node=None):
        """Obtiene una experiencia específica por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT * FROM Vista_Experiencia 
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            results = self.execute_query(query, (id_hospital, id_personal), node=current_node)
            
            if results and len(results) > 0:
                return results[0]
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo experiencia: {e}")
            return None
    
    def create_experiencia(self, experiencia_data, node=None):
        """Crea una nueva experiencia en Vista_Experiencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                INSERT INTO Vista_Experiencia 
                (ID_Hospital, ID_Personal, Cargo, Años_exp)
                VALUES (?, ?, ?, ?)
            """
            
            params = (
                experiencia_data['ID_Hospital'],
                experiencia_data['ID_Personal'],
                experiencia_data['Cargo'],
                experiencia_data['Años_exp']
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Experiencia creada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar la experiencia'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear experiencia: {str(e)}'
            }
    
    def update_experiencia(self, id_hospital, id_personal, experiencia_data, node=None):
        """Actualiza una experiencia existente en Vista_Experiencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Vista_Experiencia 
                SET Cargo = ?, Años_exp = ?
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
            params = (
                experiencia_data['Cargo'],
                experiencia_data['Años_exp'],
                id_hospital,
                id_personal
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Experiencia actualizada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar la experiencia (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar experiencia: {str(e)}'
            }
    
    def delete_experiencia(self, id_hospital, id_personal, node=None):
        """Elimina una experiencia de Vista_Experiencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Vista_Experiencia 
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
            result = self.execute_query(query, (id_hospital, id_personal), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Experiencia eliminada exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar la experiencia (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar experiencia: {str(e)}'
            }
    
    def search_experiencias(self, search_term, node=None):
        """Busca experiencias por cargo, ID_Personal o años de experiencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'experiencias': []
                }
            
            query = """
                SELECT * FROM Vista_Experiencia 
                WHERE Cargo LIKE ? OR 
                      CAST(ID_Personal AS VARCHAR) LIKE ? OR 
                      CAST(Años_exp AS VARCHAR) LIKE ?
                ORDER BY ID_Hospital, ID_Personal
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (search_pattern, search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'experiencias': []
                }
            
            return {
                'success': True,
                'experiencias': results,
                'node': current_node,
                'total': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'experiencias': []
            }
