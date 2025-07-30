from .base import DatabaseConnection

class AtencionMedicaModel(DatabaseConnection):
    """Modelo para manejar operaciones con Vista_Atencion_Medica"""
    
    def __init__(self):
        super().__init__()
    
    def get_all_atenciones(self, node=None):
        """Obtiene todas las atenciones médicas desde Vista_Atencion_Medica filtrado por nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'atenciones': [],
                    'node': None,
                    'total': 0
                }
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
            SELECT * FROM Vista_Atencion_Medica 
            WHERE ID_Hospital = ?
            ORDER BY ID_Atención
            """
            results = self.execute_query(query, params=[hospital_id], node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and isinstance(results, list) and len(results) > 0:
                print(f"Atenciones médicas filtradas para nodo {current_node} (Hospital {hospital_id}): {len(results)} registros")
                print(f"Primer registro: {results[0]}")
            
            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Vista_Atencion_Medica en nodo {current_node}',
                    'atenciones': [],
                    'node': current_node,
                    'total': 0
                }
            
            # Formatear fechas para el frontend
            if isinstance(results, list):
                for atencion in results:
                    if atencion.get('Fecha'):
                        fecha = atencion['Fecha']
                        if hasattr(fecha, 'strftime'):
                            atencion['Fecha'] = fecha.strftime('%d/%m/%Y')
            
            return {
                'success': True,
                'atenciones': results,
                'node': current_node,
                'total': len(results) if isinstance(results, list) else 0,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'atenciones': [],
                'node': current_node if 'current_node' in locals() else None,
                'total': 0
            }
    
    def get_atencion_by_id(self, id_hospital, id_atencion, node=None):
        """Obtiene una atención médica específica por ID"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return None
            
            query = """
                SELECT * FROM Vista_Atencion_Medica 
                WHERE ID_Hospital = ? AND ID_Atención = ?
            """
            results = self.execute_query(query, (id_hospital, id_atencion), node=current_node)
            
            if results and len(results) > 0:
                atencion = results[0]
                # Formatear fecha
                if atencion.get('Fecha'):
                    fecha = atencion['Fecha']
                    if hasattr(fecha, 'strftime'):
                        atencion['Fecha'] = fecha.strftime('%d/%m/%Y')
                
                return atencion
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo atención médica: {e}")
            return None
    
    def create_atencion(self, atencion_data, node=None):
        """Crea una nueva atención médica en Vista_Atencion_Medica"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                INSERT INTO Vista_Atencion_Medica 
                (ID_Hospital, ID_Atención, ID_Paciente, ID_Personal, ID_Tipo, 
                 Fecha, Diagnostico, Descripción, Tratamiento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                atencion_data['ID_Hospital'],
                atencion_data['ID_Atención'],
                atencion_data['ID_Paciente'],
                atencion_data['ID_Personal'],
                atencion_data['ID_Tipo'],
                atencion_data['Fecha'],
                atencion_data['Diagnostico'],
                atencion_data['Descripción'],
                atencion_data['Tratamiento']
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Atención médica creada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo insertar la atención médica'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear atención médica: {str(e)}'
            }
    
    def update_atencion(self, id_hospital, id_atencion, atencion_data, node=None):
        """Actualiza una atención médica existente en Vista_Atencion_Medica"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                UPDATE Vista_Atencion_Medica 
                SET ID_Paciente = ?, ID_Personal = ?, ID_Tipo = ?, 
                    Fecha = ?, Diagnostico = ?, Descripción = ?, Tratamiento = ?
                WHERE ID_Hospital = ? AND ID_Atención = ?
            """
            
            params = (
                atencion_data['ID_Paciente'],
                atencion_data['ID_Personal'],
                atencion_data['ID_Tipo'],
                atencion_data['Fecha'],
                atencion_data['Diagnostico'],
                atencion_data['Descripción'],
                atencion_data['Tratamiento'],
                id_hospital,
                id_atencion
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Atención médica actualizada exitosamente en nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo actualizar la atención médica (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar atención médica: {str(e)}'
            }
    
    def delete_atencion(self, id_hospital, id_atencion, node=None):
        """Elimina una atención médica de Vista_Atencion_Medica"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            query = """
                DELETE FROM Vista_Atencion_Medica 
                WHERE ID_Hospital = ? AND ID_Atención = ?
            """
            
            result = self.execute_query(query, (id_hospital, id_atencion), node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Atención médica eliminada exitosamente del nodo {current_node}'
                }
            else:
                return {
                    'success': False,
                    'error': 'No se pudo eliminar la atención médica (puede que no exista)'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar atención médica: {str(e)}'
            }
    
    def search_atenciones(self, search_term, node=None):
        """Busca atenciones médicas por ID de paciente, personal o atención (filtrado por nodo)"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'atenciones': []
                }
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
                SELECT * FROM Vista_Atencion_Medica 
                WHERE ID_Hospital = ? AND (
                    CAST(ID_Paciente AS VARCHAR) LIKE ? OR 
                    CAST(ID_Personal AS VARCHAR) LIKE ? OR 
                    CAST(ID_Atención AS VARCHAR) LIKE ? OR
                    Diagnostico LIKE ? OR
                    Descripción LIKE ? OR
                    Tratamiento LIKE ?
                )
                ORDER BY Fecha DESC
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (hospital_id, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'atenciones': []
                }
            
            # Formatear fechas
            if isinstance(results, list):
                for atencion in results:
                    if atencion.get('Fecha'):
                        fecha = atencion['Fecha']
                        if hasattr(fecha, 'strftime'):
                            atencion['Fecha'] = fecha.strftime('%d/%m/%Y')
            
            return {
                'success': True,
                'atenciones': results,
                'node': current_node,
                'total': len(results) if isinstance(results, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'atenciones': []
            }
