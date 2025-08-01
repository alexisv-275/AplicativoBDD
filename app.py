from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models.pacientes import PacientesModel
from models.atencion_medica import AtencionMedicaModel
from models.experiencia import ExperienciaModel
from models.especialidad import EspecialidadModel
from models.tipo_atencion import TipoAtencionModel
from models.personal_medico import PersonalMedicoModel
from models.contratos import ContratosManager
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

# Instancias de los modelos
pacientes_model = PacientesModel()
atencion_medica_model = AtencionMedicaModel()
experiencia_model = ExperienciaModel()
especialidad_model = EspecialidadModel()
tipo_atencion_model = TipoAtencionModel()
personal_medico_model = PersonalMedicoModel()

@app.route('/')
def index():
    """Página principal del sistema hospitalario"""
    return render_template('index.html')

@app.route('/hospital')
def hospital():
    """Pantalla de presentación del hospital"""
    return render_template('hospital.html')

@app.route('/pacientes')
def pacientes():
    """Módulo de gestión de pacientes - Carga desde Vista_Paciente"""
    try:
        result = pacientes_model.get_all_pacientes()
        
        return render_template('pacientes.html', 
                             pacientes=result['pacientes'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar pacientes: {str(e)}', 'error')
        return render_template('pacientes.html', 
                             pacientes=[], 
                             current_node='quito')

@app.route('/api/pacientes')
def api_pacientes():
    """API para obtener pacientes en formato JSON"""
    try:
        result = pacientes_model.get_all_pacientes()
        
        if result['success']:
            return jsonify({
                'success': True,
                'node': result['node'],
                'pacientes': result['pacientes'],
                'total': result['total']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'node': result['node']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/pacientes/add', methods=['POST'])
def api_add_paciente():
    """API para agregar nuevo paciente con auto-asignación de ID"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG API: Datos recibidos para crear paciente: {data}")
        
        # Validar datos requeridos
        required_fields = ['Nombre', 'Apellido', 'Direccion', 'FechaNacimiento', 'Sexo', 'Telefono']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False, 
                    'error': f'Campo requerido faltante: {field}'
                })
        
        result = pacientes_model.create_paciente(data)
        print(f"🔍 DEBUG API: Resultado creación paciente: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API crear paciente: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/<int:id_hospital>/<int:id_paciente>', methods=['PUT'])
def api_update_paciente(id_hospital, id_paciente):
    """API para actualizar un paciente usando stored procedure"""
    try:
        data = request.get_json()
        print(f"🔧 DEBUG API: Actualizando paciente H={id_hospital}, P={id_paciente}, Datos: {data}")
        
        # Validar datos requeridos
        required_fields = ['Nombre', 'Apellido', 'Direccion', 'FechaNacimiento', 'Sexo', 'Telefono']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'error': f'Campo requerido faltante: {field}'
                })
        
        result = pacientes_model.update_paciente(id_hospital, id_paciente, data)
        print(f"🔧 DEBUG API: Resultado actualización: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API actualizar paciente: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/<int:id_hospital>/<int:id_paciente>', methods=['DELETE'])
def api_delete_paciente(id_hospital, id_paciente):
    """API para eliminar un paciente usando stored procedure"""
    try:
        print(f"🗑️ DEBUG API: Eliminando paciente H={id_hospital}, P={id_paciente}")
        
        result = pacientes_model.delete_paciente(id_hospital, id_paciente)
        print(f"🗑️ DEBUG API: Resultado eliminación: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API eliminar paciente: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/search')
def api_search_pacientes():
    """API para buscar pacientes (filtrado por hospital local)"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'})
        
        print(f"🔍 DEBUG API: Buscando pacientes con término: '{query}'")
        result = pacientes_model.search_pacientes(query)
        print(f"🔍 DEBUG API: Resultado búsqueda: {result.get('total', 0)} pacientes encontrados")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API buscar pacientes: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/pacientes/<int:id_hospital>/<int:id_paciente>', methods=['GET'])
def api_get_paciente(id_hospital, id_paciente):
    """API para obtener un paciente específico por ID"""
    try:
        print(f"🔍 DEBUG API: Obteniendo paciente H={id_hospital}, P={id_paciente}")
        
        paciente = pacientes_model.get_paciente_by_id(id_hospital, id_paciente)
        
        if paciente:
            return jsonify({
                'success': True,
                'paciente': paciente
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Paciente no encontrado'
            })
            
    except Exception as e:
        print(f"❌ ERROR API obtener paciente: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/citas')
def citas():
    """Módulo de atención médica y citas - Carga desde Vista_Atencion_Medica"""
    try:
        result = atencion_medica_model.get_all_atenciones()
        
        return render_template('citas.html', 
                             atenciones=result['atenciones'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar atenciones médicas: {str(e)}', 'error')
        return render_template('citas.html', 
                             atenciones=[], 
                             current_node='quito')

@app.route('/api/atenciones')
def api_atenciones():
    """API para obtener atenciones médicas en formato JSON"""
    try:
        result = atencion_medica_model.get_all_atenciones()
        
        if result['success']:
            return jsonify({
                'success': True,
                'node': result['node'],
                'atenciones': result['atenciones'],
                'total': result['total']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'node': result['node']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/atenciones/add', methods=['POST'])
def api_add_atencion():
    """API para agregar nueva atención médica"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG API: Datos recibidos para crear atención médica: {data}")
        # Validar datos requeridos
        required_fields = ['ID_Personal', 'ID_Paciente', 'ID_Tipo', 'Fecha', 'Diagnostico', 'Descripción', 'Tratamiento']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                })
        result = atencion_medica_model.create_atencion_medica(data)
        print(f"🔍 DEBUG API: Resultado creación atención: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR API crear atención médica: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/atenciones/<int:id_hospital>/<int:id_atencion>', methods=['PUT'])
def api_update_atencion(id_hospital, id_atencion):
    """API para actualizar una atención médica"""
    try:
        data = request.get_json()
        print(f"🔧 DEBUG API: Actualizando atención H={id_hospital}, A={id_atencion}, Datos: {data}")
        required_fields = ['ID_Personal', 'ID_Paciente', 'ID_Tipo', 'Fecha', 'Diagnostico', 'Descripción', 'Tratamiento']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                })
        result = atencion_medica_model.update_atencion_medica(id_hospital, id_atencion, data)
        print(f"🔧 DEBUG API: Resultado actualización: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR API actualizar atención médica: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/atenciones/<int:id_hospital>/<int:id_atencion>', methods=['DELETE'])
def api_delete_atencion(id_hospital, id_atencion):
    """API para eliminar una atención médica"""
    try:
        print(f"🗑️ DEBUG API: Eliminando atención H={id_hospital}, A={id_atencion}")
        result = atencion_medica_model.delete_atencion_medica(id_hospital, id_atencion)
        print(f"🗑️ DEBUG API: Resultado eliminación: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"❌ ERROR API eliminar atención médica: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/atenciones/search')
def api_search_atenciones():
    """API para buscar atenciones médicas"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'})
        
        result = atencion_medica_model.search_atenciones(query)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/personal')
def personal():
    """Módulo de gestión de personal médico - Carga desde Vista_INF_Personal"""
    try:
        result = personal_medico_model.get_all_personal_medico()
        
        return render_template('personal.html', 
                             personal_medico=result['personal_medico'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar personal médico: {str(e)}', 'error')
        return render_template('personal.html', 
                             personal_medico=[], 
                             current_node='quito')

@app.route('/api/personal-medico')
def api_personal_medico():
    """API para obtener personal médico en formato JSON"""
    try:
        result = personal_medico_model.get_all_personal_medico()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/personal-medico/search')
def api_search_personal_medico():
    """API para buscar personal médico"""
    try:
        search_term = request.args.get('q', '')
        result = personal_medico_model.search_personal_medico(search_term)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'personal_medico': []
        })

@app.route('/api/personal-medico/add', methods=['POST'])
def api_add_personal_medico():
    """API para agregar un nuevo personal médico"""
    try:
        data = request.get_json()
        result = personal_medico_model.create_personal_medico(data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/personal-medico/<int:id_hospital>/<int:id_personal>', methods=['PUT'])
def api_update_personal_medico(id_hospital, id_personal):
    """API para actualizar un personal médico usando SP"""
    try:
        data = request.get_json()
        
        print(f"🔧 DEBUG UPDATE - IDs: hospital={id_hospital}, personal={id_personal}")
        print(f"🔧 DEBUG UPDATE - Datos recibidos: {data}")
        
        if not data:
            print("❌ ERROR: No se recibieron datos")
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
        
        # Verificar campos requeridos
        required_fields = ['ID_Especialidad', 'Nombre', 'Apellido']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            print(f"❌ ERROR: Campos faltantes: {missing_fields}")
            return jsonify({
                'success': False,
                'error': f'Campos obligatorios faltantes: {", ".join(missing_fields)}'
            }), 400
        
        result = personal_medico_model.update_personal_medico_sp(id_hospital, id_personal, data)
        
        print(f"🔧 DEBUG UPDATE - Resultado: {result}")
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"💥 ERROR en UPDATE: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/personal-medico/<int:id_hospital>/<int:id_personal>', methods=['DELETE'])
def api_delete_personal_medico(id_hospital, id_personal):
    """API para eliminar un personal médico Y su contrato asociado (consistencia)"""
    try:
        print(f'🗑️ DEBUG DELETE - IDs: hospital={id_hospital}, personal={id_personal}')
        
        # Usar el método que elimina Personal Médico + Contrato para mantener consistencia
        result = personal_medico_model.delete_personal_medico_with_contrato(id_hospital, id_personal)
        
        print(f'🗑️ DEBUG DELETE - Resultado: {result}')
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f'💥 ERROR DELETE: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/personal-medico-with-contrato', methods=['POST'])
def api_create_personal_medico_with_contrato():
    """API para crear personal médico + contrato integrado"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
            
        personal_data = data.get('personal_data')
        salario = data.get('salario')
        fecha_contrato = data.get('fecha_contrato')
        
        if not personal_data or not salario:
            return jsonify({
                'success': False,
                'error': 'Faltan datos requeridos (personal_data y salario)'
            }), 400
        
        # Crear personal médico + contrato
        result = personal_medico_model.create_personal_medico_with_contrato(
            personal_data, salario, fecha_contrato
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RUTAS DE CONTRATOS ====================

@app.route('/contratos')
def contratos():
    """Módulo de contratos - Carga desde tabla Contratos"""
    try:
        contratos_manager = ContratosManager()
        contratos = contratos_manager.get_all_contratos()
        current_node = "Quito" if len(contratos) > 0 and contratos[0].get('ID_Hospital') == 1 else "Guayaquil"
        
        return render_template('contratos.html', 
                             contratos=contratos,
                             current_node=current_node)
        
    except Exception as e:
        flash(f'Error al cargar contratos: {str(e)}', 'error')
        return render_template('contratos.html', contratos=[])

@app.route('/api/contratos')
def api_contratos():
    """API para obtener todos los contratos"""
    try:
        contratos_manager = ContratosManager()
        contratos = contratos_manager.get_all_contratos()
        
        return jsonify({
            'success': True,
            'contratos': contratos,
            'total': len(contratos)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'contratos': []
        }), 500

@app.route('/api/contratos/search')
def api_search_contratos():
    """API para buscar contratos"""
    try:
        search_term = request.args.get('q', '')
        contratos_manager = ContratosManager()
        contratos = contratos_manager.search_contratos(search_term)
        
        return jsonify({
            'success': True,
            'contratos': contratos,
            'total': len(contratos)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'contratos': []
        }), 500

@app.route('/api/contratos/add', methods=['POST'])
def api_add_contrato():
    """API para agregar un nuevo contrato"""
    try:
        data = request.get_json()
        contratos_manager = ContratosManager()
        
        result = contratos_manager.create_contrato(
            data['id_hospital'],
            data['id_personal'],
            data['salario'],
            data.get('fecha_contrato')
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Contrato creado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'Error al crear contrato'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contratos/<int:id_hospital>/<int:id_personal>', methods=['PUT'])
def api_update_contrato(id_hospital, id_personal):
    """API para actualizar un contrato"""
    try:
        data = request.get_json()
        contratos_manager = ContratosManager()
        
        result = contratos_manager.update_contrato(
            id_hospital,
            id_personal,
            data['salario'],
            data.get('fecha_contrato')
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Contrato actualizado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contratos/<int:id_hospital>/<int:id_personal>', methods=['DELETE'])
def api_delete_contrato(id_hospital, id_personal):
    """API para eliminar un contrato"""
    try:
        contratos_manager = ContratosManager()
        result = contratos_manager.delete_contrato(id_hospital, id_personal)
        
        if result:
            return jsonify({'success': True, 'message': 'Contrato eliminado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'Contrato no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/experiencia')
def experiencia():
    """Módulo de experiencia médica - Carga desde Vista_Experiencia"""
    try:
        result = experiencia_model.get_all_experiencias()
        
        return render_template('experiencia.html', 
                             experiencias=result['experiencias'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar experiencias: {str(e)}', 'error')
        return render_template('experiencia.html', 
                             experiencias=[], 
                             current_node='quito')

@app.route('/api/experiencias')
def api_experiencias():
    """API para obtener experiencias en formato JSON"""
    try:
        result = experiencia_model.get_all_experiencias()
        
        if result['success']:
            return jsonify({
                'success': True,
                'node': result['node'],
                'experiencias': result['experiencias'],
                'total': result['total']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'node': result['node']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/experiencias/add', methods=['POST'])
def api_add_experiencia():
    """API para agregar nueva experiencia con ID_Personal específico"""
    try:
        data = request.get_json()
        print(f"🔍 DEBUG API: Datos recibidos para crear experiencia: {data}")
        
        # Validar datos requeridos
        required_fields = ['ID_Personal', 'Cargo', 'Anios_exp']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False, 
                    'error': f'Campo requerido faltante: {field}'
                })
        
        result = experiencia_model.create_experiencia(data)
        print(f"🔍 DEBUG API: Resultado creación experiencia: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API crear experiencia: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiencias/<int:id_hospital>/<int:id_personal>', methods=['PUT'])
def api_update_experiencia(id_hospital, id_personal):
    """API para actualizar una experiencia usando stored procedure"""
    try:
        data = request.get_json()
        print(f"🔧 DEBUG API: Actualizando experiencia H={id_hospital}, P={id_personal}, Datos: {data}")
        
        # Validar datos requeridos
        required_fields = ['Cargo', 'Anios_exp']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False, 
                    'error': f'Campo requerido faltante: {field}'
                })
        
        result = experiencia_model.update_experiencia(id_hospital, id_personal, data)
        print(f"🔧 DEBUG API: Resultado actualización: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API actualizar experiencia: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiencias/<int:id_hospital>/<int:id_personal>/<cargo>', methods=['DELETE'])
def api_delete_experiencia(id_hospital, id_personal, cargo):
    """API para eliminar una experiencia usando stored procedure"""
    try:
        print(f"🗑️ DEBUG API: Eliminando experiencia H={id_hospital}, P={id_personal}, Cargo={cargo}")
        
        result = experiencia_model.delete_experiencia(id_hospital, id_personal, cargo)
        print(f"🗑️ DEBUG API: Resultado eliminación: {result}")
        
        return jsonify(result)
            
    except Exception as e:
        print(f"❌ ERROR API eliminar experiencia: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiencias/search')
def api_search_experiencias():
    """API para buscar experiencias"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'})
        
        result = experiencia_model.search_experiencias(query)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/especialidad')
def especialidad():
    """Módulo de especialidades médicas - Carga desde tabla Especialidad"""
    try:
        result = especialidad_model.get_all_especialidades()
        
        return render_template('especialidad.html', 
                             especialidades=result['especialidades'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar especialidades: {str(e)}', 'error')
        return render_template('especialidad.html', 
                             especialidades=[], 
                             current_node='quito')

@app.route('/api/especialidades')
def api_especialidades():
    """API para obtener especialidades en formato JSON"""
    try:
        result = especialidad_model.get_all_especialidades()
        
        if result['success']:
            return jsonify({
                'success': True,
                'node': result['node'],
                'especialidades': result['especialidades'],
                'total': result['total']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'node': result['node']
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/especialidades/add', methods=['POST'])
def api_add_especialidad():
    """API para agregar nueva especialidad"""
    try:
        data = request.get_json()
        print(f'➕ DEBUG CREATE ESPECIALIDAD - Datos recibidos: {data}')
        
        result = especialidad_model.create_especialidad(data)
        print(f'➕ DEBUG CREATE ESPECIALIDAD - Resultado: {result}')
        
        return jsonify(result)
            
    except Exception as e:
        print(f'💥 ERROR CREATE ESPECIALIDAD: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/especialidades/<int:id_especialidad>', methods=['PUT'])
def api_update_especialidad(id_especialidad):
    """API para actualizar una especialidad"""
    try:
        data = request.get_json()
        print(f'🔧 DEBUG UPDATE ESPECIALIDAD - ID: {id_especialidad}, Datos: {data}')
        
        result = especialidad_model.update_especialidad(id_especialidad, data)
        print(f'🔧 DEBUG UPDATE ESPECIALIDAD - Resultado: {result}')
        
        return jsonify(result)
            
    except Exception as e:
        print(f'💥 ERROR UPDATE ESPECIALIDAD: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/especialidades/<int:id_especialidad>', methods=['DELETE'])
def api_delete_especialidad(id_especialidad):
    """API para eliminar una especialidad"""
    try:
        print(f'🗑️ DEBUG DELETE ESPECIALIDAD - ID: {id_especialidad}')
        
        result = especialidad_model.delete_especialidad(id_especialidad)
        print(f'🗑️ DEBUG DELETE ESPECIALIDAD - Resultado: {result}')
        
        return jsonify(result)
            
    except Exception as e:
        print(f'💥 ERROR DELETE ESPECIALIDAD: {e}')
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/especialidades/search')
def api_search_especialidades():
    """API para buscar especialidades"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'})
        
        result = especialidad_model.search_especialidades(query)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/tipo-atencion')
def tipo_atencion():
    """Módulo de gestión de tipos de atención - Carga desde tabla Tipo_Atención"""
    try:
        result = tipo_atencion_model.get_all_tipos_atencion()
        
        return render_template('tipo_atencion.html', 
                             tipos_atencion=result['tipos_atencion'] if result['success'] else [],
                             current_node=result['node'])
    except Exception as e:
        flash(f'Error al cargar tipos de atención: {str(e)}', 'error')
        return render_template('tipo_atencion.html', 
                             tipos_atencion=[], 
                             current_node='quito')

@app.route('/api/tipos-atencion')
def api_tipos_atencion():
    """API para obtener tipos de atención en formato JSON"""
    try:
        result = tipo_atencion_model.get_all_tipos_atencion()
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'node': 'unknown'
        })

@app.route('/api/tipos-atencion/search')
def api_search_tipos_atencion():
    """API para buscar tipos de atención"""
    try:
        search_term = request.args.get('q', '')
        result = tipo_atencion_model.search_tipos_atencion(search_term)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tipos_atencion': []
        })

@app.route('/api/tipos-atencion/add', methods=['POST'])
def api_add_tipo_atencion():
    """API para agregar un nuevo tipo de atención"""
    try:
        data = request.get_json()
        print(f'➕ DEBUG CREATE TIPO ATENCIÓN - Datos recibidos: {data}')
        
        result = tipo_atencion_model.create_tipo_atencion(data)
        print(f'➕ DEBUG CREATE TIPO ATENCIÓN - Resultado: {result}')
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f'💥 ERROR CREATE TIPO ATENCIÓN: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tipos-atencion/<int:id_tipo>', methods=['PUT'])
def api_update_tipo_atencion(id_tipo):
    """API para actualizar un tipo de atención"""
    try:
        data = request.get_json()
        print(f'🔧 DEBUG UPDATE TIPO ATENCIÓN - ID: {id_tipo}, Datos: {data}')
        
        result = tipo_atencion_model.update_tipo_atencion(id_tipo, data)
        print(f'🔧 DEBUG UPDATE TIPO ATENCIÓN - Resultado: {result}')
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f'💥 ERROR UPDATE TIPO ATENCIÓN: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tipos-atencion/<int:id_tipo>', methods=['DELETE'])
def api_delete_tipo_atencion(id_tipo):
    """API para eliminar un tipo de atención"""
    try:
        print(f'🗑️ DEBUG DELETE TIPO ATENCIÓN - ID: {id_tipo}')
        
        result = tipo_atencion_model.delete_tipo_atencion(id_tipo)
        print(f'🗑️ DEBUG DELETE TIPO ATENCIÓN - Resultado: {result}')
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f'💥 ERROR DELETE TIPO ATENCIÓN: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

