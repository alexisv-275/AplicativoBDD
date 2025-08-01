from .base import DatabaseConnection

class ExperienciaModel(DatabaseConnection):
    # Configuración de rangos de ID_Personal por nodo
    ID_RANGES = {
        'quito': {'min': 1, 'max': 10},
        'guayaquil': {'min': 11, 'max': 20}
    }

    def get_next_available_id(self, node=None):
        current_node = node or self.detect_current_node()
        if not current_node or current_node not in self.ID_RANGES:
            return None
        range_config = self.ID_RANGES[current_node]
        hospital_id = 1 if current_node == 'quito' else 2
        query = """
            SELECT ID_Personal FROM Vista_Experiencia
            WHERE ID_Hospital = ? AND ID_Personal BETWEEN ? AND ?
            ORDER BY ID_Personal
        """
        params = (hospital_id, range_config['min'], range_config['max'])
        results = self.execute_query(query, params, node=current_node)
        if results is None:
            return range_config['min']
        occupied_ids = {row['ID_Personal'] for row in results}
        for id_candidate in range(range_config['min'], range_config['max'] + 1):
            if id_candidate not in occupied_ids:
                return id_candidate
        return None

    def get_hospital_id_by_node(self, node=None):
        current_node = node or self.detect_current_node()
        return 1 if current_node == 'quito' else 2

    def create_experiencia(self, experiencia_data, node=None):
        """Crea una nueva experiencia usando SP con validaciones de rango y existencia"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            
            # Validar que se proporcione ID_Personal
            if 'ID_Personal' not in experiencia_data:
                return {'success': False, 'error': 'ID_Personal es requerido'}
            
            id_personal = int(experiencia_data['ID_Personal'])
            
            # Validar rango de ID_Personal según nodo
            range_config = self.ID_RANGES.get(current_node, {})
            if not (range_config['min'] <= id_personal <= range_config['max']):
                return {'success': False, 'error': f'ID_Personal debe estar entre {range_config["min"]} y {range_config["max"]} para el nodo {current_node}'}
            
            hospital_id = self.get_hospital_id_by_node(current_node)
            
            # Validar que el personal médico exista (consultando Vista_Personal_Medico o similar)
            # Nota: Esta validación se podría mejorar con una consulta específica
            
            query = "{CALL SP_Create_Experiencia (?, ?, ?, ?)}"
            params = (hospital_id, id_personal, experiencia_data['Cargo'], experiencia_data['Años_exp'] if 'Años_exp' in experiencia_data else experiencia_data['Anios_exp'])
            connection = self.get_connection(node=current_node)
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🔍 DEBUG: Creando experiencia ID_Personal={id_personal}, Hospital={hospital_id}, Nodo={current_node}, Cargo={experiencia_data['Cargo']}")
            cursor.execute(query, params)
            # Forzar la propagación de errores de SQL Server
            while cursor.nextset():
                pass
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': f'Experiencia creada exitosamente en nodo {current_node}', 'id_personal': id_personal, 'id_hospital': hospital_id}
        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN SP_Create_Experiencia ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            # Mensaje genérico para el usuario, error real solo en terminal
            return {'success': False, 'error': 'No se pudo crear la experiencia. Verifique que el ID_Personal existe en el sistema.'}

    def update_experiencia(self, id_hospital, id_personal, experiencia_data, node=None):
        """Actualiza una experiencia existente usando SP"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            query = "{CALL SP_Update_Experiencia (?, ?, ?, ?)}"
            params = (id_hospital, id_personal, experiencia_data['Cargo'], experiencia_data['Años_exp'] if 'Años_exp' in experiencia_data else experiencia_data['Anios_exp'])
            connection = self.get_connection(node=current_node)
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🔧 DEBUG: Actualizando experiencia Hospital={id_hospital}, ID_Personal={id_personal}, Cargo={experiencia_data['Cargo']}")
            cursor.execute(query, params)
            # Forzar la propagación de errores de SQL Server
            while cursor.nextset():
                pass
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': 'Experiencia actualizada exitosamente'}
        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN SP_Update_Experiencia ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            # Mensaje genérico para el usuario, error real solo en terminal
            return {'success': False, 'error': 'No se pudo actualizar la experiencia. Verifique que los datos sean válidos.'}

    def delete_experiencia(self, id_hospital, id_personal, cargo, node=None):
        """Elimina una experiencia usando SP"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {'success': False, 'error': 'No se puede conectar a ningún nodo'}
            query = "{CALL SP_Delete_Experiencia (?, ?, ?)}"
            params = (id_hospital, id_personal, cargo)
            connection = self.get_connection(node=current_node)
            if not connection:
                return {'success': False, 'error': 'No se pudo establecer conexión'}
            cursor = connection.cursor()
            print(f"🗑️ DEBUG: Eliminando experiencia Hospital={id_hospital}, ID_Personal={id_personal}, Cargo={cargo}")
            cursor.execute(query, params)
            # Forzar la propagación de errores de SQL Server
            while cursor.nextset():
                pass
            connection.commit()
            cursor.close()
            connection.close()
            return {'success': True, 'message': 'Experiencia eliminada exitosamente'}
        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN SP_Delete_Experiencia ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            # Mensaje genérico para el usuario, error real solo en terminal
            return {'success': False, 'error': 'No se pudo eliminar la experiencia. Puede que no exista o esté siendo referenciada en otra tabla.'}

    def __init__(self):
        super().__init__()
    
    def get_all_experiencias(self, node=None):
        """Obtiene todas las experiencias desde Vista_Experiencia filtrado por nodo"""
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
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
            SELECT * FROM Vista_Experiencia 
            WHERE ID_Hospital = ?
            ORDER BY ID_Personal
            """
            results = self.execute_query(query, params=[hospital_id], node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and isinstance(results, list) and len(results) > 0:
                print(f"Experiencias filtradas para nodo {current_node} (Hospital {hospital_id}): {len(results)} registros")
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
                'total': len(results) if isinstance(results, list) else 0,
                'error': None
            }
            
        except Exception as e:
            current_node = None  # Asegurar que la variable esté definida
            return {
                'success': False,
                'error': str(e),
                'experiencias': [],
                'node': current_node,
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
            
            if results and isinstance(results, list) and len(results) > 0:
                return results[0]
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo experiencia: {e}")
            return None
    
    
    def search_experiencias(self, search_term, node=None):
        """Busca experiencias por cargo, ID_Personal o años de experiencia (filtrado por nodo)"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'experiencias': []
                }
            
            # Determinar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
                SELECT * FROM Vista_Experiencia 
                WHERE ID_Hospital = ? AND (
                    Cargo LIKE ? OR 
                    CAST(ID_Personal AS VARCHAR) LIKE ? OR 
                    CAST(Años_exp AS VARCHAR) LIKE ?
                )
                ORDER BY ID_Personal
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (hospital_id, search_pattern, search_pattern, search_pattern), node=current_node)
            
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
                'total': len(results) if isinstance(results, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'experiencias': []
            }
