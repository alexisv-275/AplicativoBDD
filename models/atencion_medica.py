from .base import DatabaseConnection

class AtencionMedicaModel(DatabaseConnection):
    """Modelo para manejar operaciones con Vista_Atencion_Medica"""
    
    def __init__(self):
        super().__init__()
        # Configuración de rangos de ID por nodo
        self.ID_RANGES = {
            'quito': {'min': 1, 'max': 40},
            'guayaquil': {'min': 41, 'max': 80}
        }

    def get_next_available_id(self, node=None):
        """Obtiene el siguiente ID disponible según el rango del nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node or current_node not in self.ID_RANGES:
                return None
            range_config = self.ID_RANGES[current_node]
            hospital_id = 1 if current_node == 'quito' else 2
            query = """
                SELECT ID_Atención 
                FROM Vista_Atencion_Medica 
                WHERE ID_Hospital = ? AND ID_Atención BETWEEN ? AND ?
                ORDER BY ID_Atención
            """
            params = (hospital_id, range_config['min'], range_config['max'])
            results = self.execute_query(query, params, node=current_node)
            if results is None:
                return range_config['min']
            occupied_ids = {row['ID_Atención'] for row in results}
            for id_candidate in range(range_config['min'], range_config['max'] + 1):
                if id_candidate not in occupied_ids:
                    return id_candidate
            return None
        except Exception as e:
            print(f"Error obteniendo siguiente ID atención: {e}")
            return None

    def get_hospital_id_by_node(self, node=None):
        current_node = node or self.detect_current_node()
        return 1 if current_node == 'quito' else 2
    
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
    
    def create_atencion_medica(self, atencion_data, node=None):
        """Crea una nueva atención médica con auto-asignación de ID según rango del nodo usando SP"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            next_id = self.get_next_available_id(current_node)
            if next_id is None:
                range_config = self.ID_RANGES.get(current_node, {})
                return {'success': False, 'error': f'No hay IDs disponibles en el rango {range_config.get("min", "?")} - {range_config.get("max", "?")} para el nodo {current_node}'}
            hospital_id = 1 if current_node == 'quito' else 2
            connection = self.get_connection()
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🔍 DEBUG: Creando atención ID={next_id}, Hospital={hospital_id}, Nodo={current_node}")
            cursor.execute("{CALL SP_Create_Atencion_Medica (?, ?, ?, ?, ?, ?, ?, ?, ?)}",
                (hospital_id, next_id, atencion_data['ID_Personal'], atencion_data['ID_Paciente'],
                 atencion_data['ID_Tipo'], atencion_data['Fecha'], atencion_data['Diagnostico'],
                 atencion_data['Descripción'], atencion_data['Tratamiento']))
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': f'Atención médica creada exitosamente en nodo {current_node}', 'id_atencion': next_id, 'id_hospital': hospital_id}
        except Exception as e:
            print(f"Error en SP_Create_Atencion_Medica: {e}")
            return {'success': False, 'error': f'Error al crear atención médica: {str(e)}'}
    
    def update_atencion_medica(self, id_hospital, id_atencion, atencion_data, node=None):
        """Actualiza una atención médica usando SP_Update_Atencion_Medica"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            connection = self.get_connection()
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🔧 DEBUG: Actualizando atención Hospital={id_hospital}, ID={id_atencion}")
            cursor.execute("{CALL SP_Update_Atencion_Medica (?, ?, ?, ?, ?, ?, ?, ?, ?)}",
                (id_hospital, id_atencion, atencion_data['ID_Personal'], atencion_data['ID_Paciente'],
                 atencion_data['ID_Tipo'], atencion_data['Fecha'], atencion_data['Diagnostico'],
                 atencion_data['Descripción'], atencion_data['Tratamiento']))
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': 'Atención médica actualizada exitosamente'}
        except Exception as e:
            print(f"Error en SP_Update_Atencion_Medica: {e}")
            return {'success': False, 'error': f'Error al actualizar atención médica: {str(e)}'}
    
    def delete_atencion_medica(self, id_hospital, id_atencion, node=None):
        """Elimina una atención médica usando SP_Delete_Atencion_Medica"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            connection = self.get_connection()
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🗑️ DEBUG: Eliminando atención Hospital={id_hospital}, ID={id_atencion}")
            cursor.execute("{CALL SP_Delete_Atencion_Medica (?, ?)}", (id_hospital, id_atencion))
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': 'Atención médica eliminada exitosamente'}
        except Exception as e:
            print(f"Error en SP_Delete_Atencion_Medica: {e}")
            return {'success': False, 'error': f'Error al eliminar atención médica: {str(e)}'}
    
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
