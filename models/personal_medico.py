from .base import DatabaseConnection

class PersonalMedicoModel(DatabaseConnection):
    """Modelo para manejar operaciones con la vista Vista_INF_Personal"""
    
    def __init__(self):
        super().__init__()
        # Configuración de rangos de ID por nodo
        self.ID_RANGES = {
            'quito': {'min': 1, 'max': 10},
            'guayaquil': {'min': 11, 'max': 20}
        }
    
    def get_next_available_id(self, node=None):
        """Obtiene el siguiente ID disponible según el rango del nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node or current_node not in self.ID_RANGES:
                return None
            
            range_config = self.ID_RANGES[current_node]
            min_id = range_config['min']
            max_id = range_config['max']
            
            # Consultar IDs existentes en el rango del nodo
            query = """
            SELECT ID_Personal 
            FROM Vista_INF_Personal 
            WHERE ID_Personal BETWEEN ? AND ?
            ORDER BY ID_Personal
            """
            
            results = self.execute_query(query, params=[min_id, max_id], node=current_node)
            
            if results is None:
                return min_id  # Si hay error, empezar desde el mínimo
            
            # Buscar el primer ID disponible en el rango
            used_ids = [row['ID_Personal'] for row in results] if results else []
            
            for id_candidate in range(min_id, max_id + 1):
                if id_candidate not in used_ids:
                    return id_candidate
            
            # Si no hay IDs disponibles en el rango
            return None
            
        except Exception as e:
            print(f"Error obteniendo siguiente ID: {e}")
            return None
    
    def validate_id_range(self, id_personal, node=None):
        """Valida que el ID esté dentro del rango permitido para el nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node or current_node not in self.ID_RANGES:
                return False
            
            range_config = self.ID_RANGES[current_node]
            return range_config['min'] <= id_personal <= range_config['max']
            
        except Exception as e:
            print(f"Error validando rango de ID: {e}")
            return False
    
    def get_all_personal_medico(self, node=None):
        """Obtiene todo el personal médico desde Vista_INF_Personal (sin filtrado por hospital)"""
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
            
            query = """
            SELECT ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono 
            FROM Vista_INF_Personal 
            ORDER BY ID_Personal
            """
            results = self.execute_query(query, node=current_node)
            
            # Debug: Ver qué campos están disponibles
            if results and len(results) > 0:
                print(f"Personal médico total: {len(results)} registros")
            
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
        """Crea un nuevo personal médico con auto-asignación de ID según rango del nodo"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # Auto-asignar ID_Personal según el rango del nodo
            next_id = self.get_next_available_id(current_node)
            if next_id is None:
                range_config = self.ID_RANGES.get(current_node, {})
                return {
                    'success': False,
                    'error': f'No hay IDs disponibles en el rango {range_config.get("min", "?")} - {range_config.get("max", "?")} para el nodo {current_node}'
                }
            
            # Auto-asignar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            query = """
                INSERT INTO Vista_INF_Personal (ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            params = (
                hospital_id,
                next_id, 
                personal_data['ID_Especialidad'],
                personal_data['Nombre'],
                personal_data['Apellido'],
                personal_data['Teléfono']
            )
            
            result = self.execute_query(query, params, node=current_node)
            
            if result is not None and result > 0:
                return {
                    'success': True,
                    'message': f'Personal médico creado exitosamente en nodo {current_node}',
                    'id_personal': next_id,
                    'id_hospital': hospital_id
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
        """Busca personal médico por nombre, apellido o ID (sin filtrado por hospital)"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo',
                    'personal_medico': []
                }
            
            query = """
                SELECT ID_Hospital, ID_Personal, ID_Especialidad, Nombre, Apellido, Teléfono
                FROM Vista_INF_Personal 
                WHERE Nombre LIKE ? OR Apellido LIKE ? OR 
                      CAST(ID_Personal AS VARCHAR) LIKE ?
                ORDER BY ID_Personal
            """
            
            search_pattern = f"%{search_term}%"
            results = self.execute_query(query, (search_pattern, search_pattern, search_pattern), node=current_node)
            
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

    def create_personal_medico_with_contrato(self, personal_data, salario, fecha_contrato=None, node=None):
        """Crear personal médico + contrato: Personal en nodo local, Contrato siempre en Quito"""
        try:
            current_node = node or self.detect_current_node()
            if not current_node:
                return {
                    'success': False,
                    'error': 'No se puede conectar a ningún nodo'
                }
            
            # Auto-asignar ID_Personal según el rango del nodo
            next_id = self.get_next_available_id(current_node)
            if next_id is None:
                range_config = self.ID_RANGES.get(current_node, {})
                return {
                    'success': False,
                    'error': f'No hay IDs disponibles en el rango {range_config.get("min", "?")} - {range_config.get("max", "?")} para el nodo {current_node}'
                }
            
            # Auto-asignar ID_Hospital según el nodo
            hospital_id = 1 if current_node == 'quito' else 2
            
            # ======================================
            # VALIDACIÓN: Verificar que NO exista contrato con este ID_Personal
            # ======================================
            from .contratos import ContratosManager
            contratos_manager = ContratosManager()
            
            # Verificar si ya existe un contrato con este ID_Personal
            contrato_existente = contratos_manager.get_contrato_by_ids(hospital_id, next_id)
            if contrato_existente:
                print(f"⚠️ CONFLICTO: Ya existe contrato para ID_Personal={next_id}, buscando siguiente ID disponible...")
                
                # Buscar siguiente ID que no tenga contrato
                range_config = self.ID_RANGES[current_node]
                for id_candidate in range(next_id + 1, range_config['max'] + 1):
                    # Verificar que no esté usado en Personal Médico
                    query = "SELECT 1 FROM Vista_INF_Personal WHERE ID_Personal = ?"
                    personal_exists = self.execute_query(query, params=[id_candidate], node=current_node)
                    
                    # Verificar que no tenga contrato
                    contrato_candidate = contratos_manager.get_contrato_by_ids(hospital_id, id_candidate)
                    
                    if not personal_exists and not contrato_candidate:
                        next_id = id_candidate
                        print(f"✅ Usando ID_Personal={next_id} (sin conflictos)")
                        break
                else:
                    return {
                        'success': False,
                        'error': f'No hay IDs disponibles sin conflictos de contratos en el rango para {current_node}'
                    }
            
            # ======================================
            # PASO 1: Crear Personal Médico en nodo local
            # ======================================
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión para insertar personal médico'
                }
                
            cursor = connection.cursor()
            
            print(f"Debug: Ejecutando SP_Create_PersonalMedico en nodo {current_node}: Hospital={hospital_id}, Personal={next_id}")
            
            # Ejecutar SP SOLO para Personal Médico (sin salario/contrato)
            cursor.execute("{CALL SP_Create_PersonalMedico (?, ?, ?, ?, ?, ?)}", 
                         (hospital_id, next_id, personal_data['ID_Especialidad'],
                          personal_data['Nombre'], personal_data['Apellido'], 
                          personal_data['Teléfono']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("Debug: Personal médico creado exitosamente")
            
            # ======================================
            # PASO 2: Crear Contrato usando conexión normal
            # ======================================
            contrato_creado = contratos_manager.create_contrato(
                hospital_id, next_id, salario, fecha_contrato
            )
            
            if not contrato_creado:
                # ROLLBACK: Si falla el contrato, eliminar el personal médico creado
                try:
                    self.delete_personal_medico_sp(hospital_id, next_id)
                    print("🔄 ROLLBACK: Personal médico eliminado debido a fallo en contrato")
                except:
                    print("⚠️ ROLLBACK FALLÓ: Personal médico creado pero contrato no. Inconsistencia detectada.")
                
                return {
                    'success': False,
                    'error': 'Falló la creación del contrato. Personal médico no creado para mantener consistencia.'
                }
            
            print("Debug: Contrato creado exitosamente en Quito")
            
            return {
                'success': True,
                'message': f'Personal médico y contrato creados exitosamente (Personal en {current_node}, Contrato en Quito)',
                'id_personal': next_id,
                'id_hospital': hospital_id
            }
            
        except Exception as e:
            print(f"Error detallado al crear personal médico + contrato: {e}")
            return {
                'success': False,
                'error': f'Error al crear personal médico + contrato: {str(e)}'
            }
            
            print("Debug: Contrato creado exitosamente en Quito")
            
            return {
                'success': True,
                'message': f'Personal médico y contrato creados exitosamente (Personal en {current_node}, Contrato en Quito)',
                'id_personal': next_id,
                'id_hospital': hospital_id
            }
            
        except Exception as e:
            print(f"Error detallado al crear personal médico + contrato: {e}")
            return {
                'success': False,
                'error': f'Error al crear personal médico + contrato: {str(e)}'
            }

    def update_personal_medico_sp(self, id_hospital, id_personal, personal_data):
        """Actualizar personal médico usando SP_Update_PersonalMedico"""
        try:
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión'
                }
                
            cursor = connection.cursor()
            
            # Ejecutar SP de actualización con transacción distribuida
            cursor.execute("{CALL SP_Update_PersonalMedico (?, ?, ?, ?, ?, ?)}", 
                         (id_hospital, id_personal, personal_data['ID_Especialidad'],
                          personal_data['Nombre'], personal_data['Apellido'], 
                          personal_data['Teléfono']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'message': 'Personal médico actualizado exitosamente'
            }
            
        except Exception as e:
            print(f"Error en SP_Update_PersonalMedico: {e}")
            return {
                'success': False,
                'error': f'Error al actualizar personal médico: {str(e)}'
            }

    def delete_personal_medico_sp(self, id_hospital, id_personal):
        """Eliminar personal médico usando SP_Delete_PersonalMedico"""
        try:
            connection = self.get_connection()
            if not connection:
                return {
                    'success': False,
                    'error': 'No se pudo establecer conexión'
                }

            cursor = connection.cursor()

            # Ejecutar SP de eliminación con transacción distribuida
            cursor.execute("{CALL SP_Delete_PersonalMedico (?, ?)}", (id_hospital, id_personal))
            # Forzar la propagación de errores de SQL Server
            while cursor.nextset():
                pass
            connection.commit()
            cursor.close()
            connection.close()

            return {
                'success': True,
                'message': 'Personal médico eliminado exitosamente'
            }

        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN SP_Delete_PersonalMedico ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            # Mensaje genérico para el usuario, error real solo en terminal
            return {
                'success': False,
                'error': 'No se pudo eliminar el personal médico. Puede que esté siendo referenciado en otra tabla.'
            }

    def delete_personal_medico_with_contrato(self, id_hospital, id_personal):
        """Eliminar personal médico Y su contrato asociado para mantener consistencia"""
        try:
            print(f"🗑️ Iniciando eliminación consistente: Personal={id_personal}, Hospital={id_hospital}")
            
            # ======================================
            # PASO 1: Verificar que el personal médico existe
            # ======================================
            personal_exists = self.get_personal_medico_by_id(id_hospital, id_personal)
            if not personal_exists:
                return {
                    'success': False,
                    'error': 'El personal médico no existe'
                }
            
            # ======================================
            # PASO 2: Eliminar contrato asociado (si existe)
            # ======================================
            from .contratos import ContratosManager
            contratos_manager = ContratosManager()
            
            contrato_existente = contratos_manager.get_contrato_by_ids(id_hospital, id_personal)
            if contrato_existente:
                print(f"🗑️ Eliminando contrato asociado para ID_Personal={id_personal}")
                contrato_eliminado = contratos_manager.delete_contrato(id_hospital, id_personal)
                if not contrato_eliminado:
                    print("⚠️ ADVERTENCIA: No se pudo eliminar el contrato, pero continuando...")
                else:
                    print("✅ Contrato eliminado exitosamente")
            else:
                print(f"ℹ️ No hay contrato asociado para ID_Personal={id_personal}")
            
            # ======================================
            # PASO 3: Eliminar personal médico
            # ======================================
            print(f"🗑️ Eliminando personal médico ID_Personal={id_personal}")
            personal_eliminado = self.delete_personal_medico_sp(id_hospital, id_personal)
            
            if personal_eliminado['success']:
                return {
                    'success': True,
                    'message': 'Personal médico y contrato eliminados exitosamente (consistencia mantenida)'
                }
            else:
                return {
                    'success': False,
                    'error': f'Error al eliminar personal médico: {personal_eliminado["error"]}'
                }
            
        except Exception as e:
            import traceback
            print("========== EXCEPCIÓN EN delete_personal_medico_with_contrato ==========")
            print(f"Tipo: {type(e)}")
            print(f"Contenido: {e}")
            print("Traceback:")
            traceback.print_exc()
            print("=====================================================")
            return {
                'success': False,
                'error': f'Error al eliminar personal médico con contrato: {str(e)}'
            }
