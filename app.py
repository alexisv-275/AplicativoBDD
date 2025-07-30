from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models.pacientes import PacientesModel
from models.atencion_medica import AtencionMedicaModel
from models.experiencia import ExperienciaModel
from models.especialidad import EspecialidadModel
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
    """API para agregar nuevo paciente"""
    try:
        data = request.get_json()
        
        result = pacientes_model.create_paciente(
            data['id_hospital'],
            data['nombre'],
            data['apellido'],
            data['direccion'],
            data['fecha_nacimiento'],
            data['sexo'],
            data['telefono']
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Paciente agregado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo agregar el paciente'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/<int:id_hospital>/<int:id_paciente>', methods=['PUT'])
def api_update_paciente(id_hospital, id_paciente):
    """API para actualizar un paciente"""
    try:
        data = request.get_json()
        
        result = pacientes_model.update_paciente(
            id_hospital,
            id_paciente,
            data['nombre'],
            data['apellido'],
            data['direccion'],
            data['fecha_nacimiento'],
            data['sexo'],
            data['telefono']
        )
        
        if result:
            return jsonify({'success': True, 'message': 'Paciente actualizado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el paciente'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/<int:id_hospital>/<int:id_paciente>', methods=['DELETE'])
def api_delete_paciente(id_hospital, id_paciente):
    """API para eliminar un paciente"""
    try:
        result = pacientes_model.delete_paciente(id_hospital, id_paciente)
        
        if result:
            return jsonify({'success': True, 'message': 'Paciente eliminado exitosamente'})
        else:
            return jsonify({'success': False, 'error': 'No se pudo eliminar el paciente'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pacientes/search')
def api_search_pacientes():
    """API para buscar pacientes"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'success': False, 'error': 'Parámetro de búsqueda requerido'})
        
        result = pacientes_model.search_pacientes(query)
        
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
        
        result = atencion_medica_model.create_atencion(data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/atenciones/<int:id_hospital>/<int:id_atencion>', methods=['PUT'])
def api_update_atencion(id_hospital, id_atencion):
    """API para actualizar una atención médica"""
    try:
        data = request.get_json()
        
        result = atencion_medica_model.update_atencion(id_hospital, id_atencion, data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/atenciones/<int:id_hospital>/<int:id_atencion>', methods=['DELETE'])
def api_delete_atencion(id_hospital, id_atencion):
    """API para eliminar una atención médica"""
    try:
        result = atencion_medica_model.delete_atencion(id_hospital, id_atencion)
        
        return jsonify(result)
            
    except Exception as e:
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
    """Módulo de personal médico"""
    return render_template('personal.html')

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
    """API para agregar nueva experiencia"""
    try:
        data = request.get_json()
        
        result = experiencia_model.create_experiencia(data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiencias/<int:id_hospital>/<int:id_personal>', methods=['PUT'])
def api_update_experiencia(id_hospital, id_personal):
    """API para actualizar una experiencia"""
    try:
        data = request.get_json()
        
        result = experiencia_model.update_experiencia(id_hospital, id_personal, data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/experiencias/<int:id_hospital>/<int:id_personal>', methods=['DELETE'])
def api_delete_experiencia(id_hospital, id_personal):
    """API para eliminar una experiencia"""
    try:
        result = experiencia_model.delete_experiencia(id_hospital, id_personal)
        
        return jsonify(result)
            
    except Exception as e:
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
        
        result = especialidad_model.create_especialidad(data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/especialidades/<int:id_especialidad>', methods=['PUT'])
def api_update_especialidad(id_especialidad):
    """API para actualizar una especialidad"""
    try:
        data = request.get_json()
        
        result = especialidad_model.update_especialidad(id_especialidad, data)
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/especialidades/<int:id_especialidad>', methods=['DELETE'])
def api_delete_especialidad(id_especialidad):
    """API para eliminar una especialidad"""
    try:
        result = especialidad_model.delete_especialidad(id_especialidad)
        
        return jsonify(result)
            
    except Exception as e:
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
    """Módulo de tipos de atención"""
    return render_template('tipo_atencion.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

