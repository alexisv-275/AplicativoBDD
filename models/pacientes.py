from .base import DatabaseConnection

class PacientesModel(DatabaseConnection):
    """Modelo para manejar operaciones con Vista_Paciente (particionada actualizable)"""
    
    def __init__(self):
        super().__init__()
        # Configuración de rangos de ID por nodo
        self.ID_RANGES = {
            'quito': {'min': 1, 'max': 20},
            'guayaquil': {'min': 21, 'max': 40}
        }
    
    def get_next_available_id(self, node=None):
        """Obtiene el siguiente ID disponible según el rango del nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node or current_node not in self.ID_RANGES:
                return None
            
            range_config = self.ID_RANGES[current_node]
            hospital_id = 1 if current_node == 'quito' else 2
            
            # Buscar IDs ocupados en el rango
            query = """
                SELECT ID_Paciente 
                FROM Vista_Paciente 
                WHERE ID_Hospital = ? AND ID_Paciente BETWEEN ? AND ?
                ORDER BY ID_Paciente
            """
            
            params = (hospital_id, range_config['min'], range_config['max'])
            results = self.execute_query(query, params, node=current_node)
            
            if results is None:
                return range_config['min']  # Si hay error, usar el mínimo
            
            # Encontrar el primer ID disponible
            occupied_ids = {row['ID_Paciente'] for row in results}
            
            for id_candidate in range(range_config['min'], range_config['max'] + 1):
                if id_candidate not in occupied_ids:
                    return id_candidate
            
            return None  # Rango completo
            
        except Exception as e:
            print(f"Error obteniendo siguiente ID paciente: {e}")
            return None
    
    def get_hospital_id_by_node(self, node=None):
        """Obtiene el ID del hospital según el nodo"""
        current_node = node or self.detect_current_node()
        return 1 if current_node == 'quito' else 2
    
    def get_all_pacientes(self, node=None):
        """Obtiene todos los pacientes desde Vista_Paciente (solo del hospital local)"""
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
            
            # 🏥 FILTRO LOCAL: Solo mostrar pacientes del hospital local
            hospital_id = self.get_hospital_id_by_node(current_node)
            
            query = """
                SELECT ID_Hospital, ID_Paciente, Nombre, Apellido, Dirección, 
                       FechaNacimiento, Sexo, Teléfono 
                FROM Vista_Paciente 
                WHERE ID_Hospital = ?
                ORDER BY ID_Paciente
            """
            
            results = self.execute_query(query, (hospital_id,), node=current_node)

            # Debug
            if results and len(results) > 0:
                print(f"🔍 DEBUG Pacientes: {len(results)} registros del hospital {hospital_id} en nodo {current_node}")

            if results is None:
                return {
                    'success': False,
                    'error': f'Error al consultar Vista_Paciente en nodo {current_node}',
                    'pacientes': [],
                    'node': current_node,
                    'total': 0
                }
            
            # Formatear fechas y mapear campos con tilde
            for paciente in results:
                # Mapear campos con tilde a nombres sin tilde para frontend
                if 'Dirección' in paciente:
                    paciente['Direccion'] = paciente['Dirección']
                if 'Teléfono' in paciente:
                    paciente['Telefono'] = paciente['Teléfono']
                    
                # Formatear fecha
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
                SELECT ID_Hospital, ID_Paciente, Nombre, Apellido, Dirección, 
                       FechaNacimiento, Sexo, Teléfono 
                FROM Vista_Paciente 
                WHERE ID_Hospital = ? AND ID_Paciente = ?
            """
            results = self.execute_query(query, (id_hospital, id_paciente), node=current_node)
            
            if results and len(results) > 0:
                paciente = results[0]
                # Mapear campos con tilde y formatear fecha
                resultado = {
                    'ID_Hospital': paciente.get('ID_Hospital'),
                    'ID_Paciente': paciente.get('ID_Paciente'),
                    'Nombre': paciente.get('Nombre'),
                    'Apellido': paciente.get('Apellido'),
                    'Direccion': paciente.get('Dirección'),  # Mapear desde BD con tilde
                    'Telefono': paciente.get('Teléfono'),    # Mapear desde BD con tilde
                    'Sexo': paciente.get('Sexo'),
                    'FechaNacimiento': None
                }
                
                # Formatear fecha
                if paciente.get('FechaNacimiento'):
                    fecha = paciente['FechaNacimiento']
                    if hasattr(fecha, 'strftime'):
                        resultado['FechaNacimiento'] = fecha.strftime('%Y-%m-%d')
                    else:
                        resultado['FechaNacimiento'] = str(fecha)
                
                return resultado
            
            return None
            
        except Exception as e:
            print(f"Error obteniendo paciente: {e}")
            return None
    
    def create_paciente(self, paciente_data, node=None):
        """Crea un nuevo paciente con auto-asignación de ID según rango del nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # Auto-asignar ID_Paciente según el rango del nodo
            next_id = self.get_next_available_id(current_node)
            if next_id is None:
                range_config = self.ID_RANGES.get(current_node, {})
                return {
                    'success': False,
                    'error': f'No hay IDs disponibles en el rango {range_config.get("min", "?")} - {range_config.get("max", "?")} para el nodo {current_node}'
                }
            
            # Auto-asignar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            # Usar stored procedure con transacción distribuida
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión'
                }
                
            cursor = connection.cursor()
            
            print(f"🔍 DEBUG: Creando paciente ID={next_id}, Hospital={hospital_id}, Nodo={current_node}")
            
            cursor.execute("{CALL SP_Create_Paciente (?, ?, ?, ?, ?, ?, ?, ?)}", 
                         (hospital_id, next_id, paciente_data['Nombre'],
                          paciente_data['Apellido'], paciente_data['Direccion'],
                          paciente_data['FechaNacimiento'], paciente_data['Sexo'],
                          paciente_data['Telefono']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'message': f'Paciente creado exitosamente en nodo {current_node}',
                'id_paciente': next_id,
                'id_hospital': hospital_id
            }
                
        except Exception as e:
            print(f"Error en SP_Create_Paciente: {e}")
            return {
                'success': False,
                'error': f'Error al crear paciente: {str(e)}'
            }
    
    def update_paciente(self, id_hospital, id_paciente, paciente_data, node=None):
        """Actualiza un paciente usando SP_Update_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # Usar stored procedure con transacción distribuida
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión'
                }
                
            cursor = connection.cursor()
            
            print(f"🔧 DEBUG: Actualizando paciente Hospital={id_hospital}, ID={id_paciente}")
            
            cursor.execute("{CALL SP_Update_Paciente (?, ?, ?, ?, ?, ?, ?, ?)}", 
                         (id_hospital, id_paciente, paciente_data['Nombre'],
                          paciente_data['Apellido'], paciente_data['Direccion'],
                          paciente_data['FechaNacimiento'], paciente_data['Sexo'],
                          paciente_data['Telefono']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'message': 'Paciente actualizado exitosamente'
            }
                
        except Exception as e:
            print(f"Error en SP_Update_Paciente: {e}")
            return {
                'success': False,
                'error': f'Error al actualizar paciente: {str(e)}'
            }
    
    def delete_paciente(self, id_hospital, id_paciente, node=None):
        """Elimina un paciente usando SP_Delete_Paciente"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # Usar stored procedure con transacción distribuida
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión'
                }
                
            cursor = connection.cursor()
            
            print(f"🗑️ DEBUG: Eliminando paciente Hospital={id_hospital}, ID={id_paciente}")
            
            cursor.execute("{CALL SP_Delete_Paciente (?, ?)}", (id_hospital, id_paciente))
            # Forzar la propagación de errores de SQL Server
            while cursor.nextset():
                pass
            connection.commit()
            cursor.close()
            connection.close()
            return {
                'success': True,
                'message': 'Paciente eliminado exitosamente'
            }
                
        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN SP_Delete_Paciente ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            # Mensaje genérico para el usuario, error real solo en terminal
            return {
                'success': False,
                'error': 'No se pudo eliminar el paciente. Puede que esté siendo referenciado en otra tabla.'
            }
    
    def search_pacientes(self, search_term, node=None):
        """Busca pacientes por nombre, apellido o ID (solo del hospital local como Experiencia)"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'pacientes': []
                }
            
            # 🏥 FILTRO LOCAL: Solo mostrar pacientes del hospital local (como Experiencia)
            hospital_id = self.get_hospital_id_by_node(current_node)
            
            query = """
                SELECT ID_Hospital, ID_Paciente, Nombre, Apellido, Dirección, 
                       FechaNacimiento, Sexo, Teléfono 
                FROM Vista_Paciente 
                WHERE ID_Hospital = ? AND (
                    Nombre LIKE ? OR Apellido LIKE ? OR 
                    CAST(ID_Paciente AS VARCHAR) LIKE ?
                )
                ORDER BY ID_Paciente
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (hospital_id, search_pattern, search_pattern, search_pattern), node=current_node)
            
            if results is None:
                return {
                    'success': False,
                    'error': 'Error en la búsqueda',
                    'pacientes': []
                }
            
            # Formatear fechas y mapear campos con tilde
            if isinstance(results, list):
                for paciente in results:
                    # Mapear campos con tilde a nombres sin tilde para frontend
                    if 'Dirección' in paciente:
                        paciente['Direccion'] = paciente['Dirección']
                    if 'Teléfono' in paciente:
                        paciente['Telefono'] = paciente['Teléfono']
                        
                    # Formatear fecha
                    if paciente.get('FechaNacimiento'):
                        fecha = paciente['FechaNacimiento']
                        if hasattr(fecha, 'strftime'):
                            paciente['FechaNacimiento'] = fecha.strftime('%d/%m/%Y')
            
            return {
                'success': True,
                'pacientes': results if isinstance(results, list) else [],
                'node': current_node,
                'hospital_id': hospital_id,
                'total': len(results) if isinstance(results, list) else 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'pacientes': []
            }
