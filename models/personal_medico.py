from .base import DatabaseConnection

class PersonalMedicoModel(DatabaseConnection):
    """Modelo para manejar operaciones con la vista Vista_INF_Personal"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_personal_medico(self, node=None):
        """Obtiene todo el personal médico desde Vista_INF_Personal filtrado por nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'personal_medico': [],
                    'node': None,
                    'total': 0
                }
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
            SELECT ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono 
            FROM Vista_INF_Personal 
            WHERE ID_Hospital = ?
            ORDER BY ID_Personal
            """
            results = self.execute_query(query, params=[hospital_id], node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and len(results) > 0:
                print(f"Personal médico filtrado para nodo {current_node} (Hospital {hospital_id}): {len(results)} registros")
                print(f"Primer registro: {results[0]}")
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Vista_INF_Personal en nodo {current_node}',
                    'personal_medico': [],
                    'node': current_node,
                    'total': 0
                }
            
            return {
                'success': True,
                'personal_medico': results,
                'node': current_node,
                'total': len(results),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'personal_medico': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_personal_medico_by_id(self, id_hospital, id_personal, node=None):
        """Obtiene un personal médico específico por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono 
                FROM Vista_INF_Personal 
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            results = self.execute_query(query, (id_hospital, id_personal), node=current_node)
            
            if results and len(results) > 0:
                return results[0]
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo personal médico: {e}")
            return None
    
    def create_personal_medico(self, personal_data, node=None):
        """Crea un nuevo personal médico en Vista_INF_Personal"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                INSERT INTO Vista_INF_Personal (ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (
                personal_data['ID_Hospital'],
                personal_data['ID_Personal'], 
                personal_data['ID_Especialidad'],
                personal_data['Nombre'],
                personal_data['Apellido'],
                personal_data['Teléfono']
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Personal médico creado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar el personal médico'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear personal médico: {str(e)}'
            }
    
    def update_personal_medico(self, id_hospital, id_personal, personal_data, node=None):
        """Actualiza un personal médico existente en Vista_INF_Personal"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Vista_INF_Personal 
                SET ID_Especialidad = ?, Nombre = ?, Apellido = ?, Teléfono = ?
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
            params = (
                personal_data['ID_Especialidad'],
                personal_data['Nombre'],
                personal_data['Apellido'],
                personal_data['Teléfono'],
                id_hospital,
                id_personal
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Personal médico actualizado exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar el personal médico (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar personal médico: {str(e)}'
            }
    
    def delete_personal_medico(self, id_hospital, id_personal, node=None):
        """Elimina un personal médico de Vista_INF_Personal"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Vista_INF_Personal 
                WHERE ID_Hospital = ? AND ID_Personal = ?
            """
            
            result = self.execute_query(query, (id_hospital, id_personal), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Personal médico eliminado exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar el personal médico (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar personal médico: {str(e)}'
            }
    
    def search_personal_medico(self, search_term, node=None):
        """Busca personal médico por nombre, apellido o ID (filtrado por nodo)"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'personal_medico': []
                }
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
                SELECT ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono
                FROM Vista_INF_Personal 
                WHERE ID_Hospital = ? AND (
                    Nombre LIKE ? OR Apellido LIKE ? OR 
                    CAST(ID_Personal AS VARCHAR) LIKE ?
                )
                ORDER BY ID_Personal
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (hospital_id, search_pattern, search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'personal_medico': []
                }
            
            return {
                'success': True,
                'personal_medico': results,
                'node': current_node,
                'total': len(results) if isinstance(results, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'personal_medico': []
            }
