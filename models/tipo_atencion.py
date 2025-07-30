from .base import DatabaseConnection

class TipoAtencionModel(DatabaseConnection):
    """Modelo para manejar operaciones con la tabla Tipo_Atención"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_tipos_atencion(self, node=None):
        """Obtiene todos los tipos de atención desde la tabla Tipo_Atención"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'tipos_atencion': [],
                    'node': None,
                    'total': 0
                }
            
            query = "SELECT ID_Tipo, Tipo FROM Tipo_Atención ORDER BY ID_Tipo"
            results = self.execute_query(query, node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and len(results) > 0:
                print(f"Campos disponibles en Tipo_Atención: {list(results[0].keys())}")
                print(f"Primer registro: {results[0]}")
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Tipo_Atención en nodo {current_node}',
                    'tipos_atencion': [],
                    'node': current_node,
                    'total': 0
                }
            
            return {
                'success': True,
                'tipos_atencion': results,
                'node': current_node,
                'total': len(results),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tipos_atencion': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_tipo_atencion_by_id(self, id_tipo, node=None):
        """Obtiene un tipo de atención específico por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT ID_Tipo, Tipo FROM Tipo_Atención 
                WHERE ID_Tipo = ?
            """
            results = self.execute_query(query, (id_tipo,), node=current_node)
            
            if results and len(results) > 0:
                return results[0]
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo tipo de atención: {e}")
            return None
    
    def create_tipo_atencion(self, tipo_atencion_data, node=None):
        """Crea un nuevo tipo de atención en la tabla Tipo_Atención"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                INSERT INTO Tipo_Atención (Tipo)
                VALUES (?)
            """
            
            params = (tipo_atencion_data['Tipo'],)
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Tipo de atención creado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar el tipo de atención'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear tipo de atención: {str(e)}'
            }
    
    def update_tipo_atencion(self, id_tipo, tipo_atencion_data, node=None):
        """Actualiza un tipo de atención existente en la tabla Tipo_Atención"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Tipo_Atención 
                SET Tipo = ?
                WHERE ID_Tipo = ?
            """
            
            params = (
                tipo_atencion_data['Tipo'],
                id_tipo
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Tipo de atención actualizado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar el tipo de atención (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar tipo de atención: {str(e)}'
            }
    
    def delete_tipo_atencion(self, id_tipo, node=None):
        """Elimina un tipo de atención de la tabla Tipo_Atención"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Tipo_Atención 
                WHERE ID_Tipo = ?
            """
            
            result = self.execute_query(query, (id_tipo,), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Tipo de atención eliminado exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar el tipo de atención (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar tipo de atención: {str(e)}'
            }
    
    def search_tipos_atencion(self, search_term, node=None):
        """Busca tipos de atención por tipo o ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'tipos_atencion': []
                }
            
            query = """
                SELECT ID_Tipo, Tipo FROM Tipo_Atención 
                WHERE Tipo LIKE ? OR 
                      CAST(ID_Tipo AS VARCHAR) LIKE ?
                ORDER BY ID_Tipo
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'tipos_atencion': []
                }
            
            return {
                'success': True,
                'tipos_atencion': results,
                'node': current_node,
                'total': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tipos_atencion': []
            }
