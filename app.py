from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models.pacientes import PacientesModel
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

# Instancia del modelo de pacientes
pacientes_model = PacientesModel()

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
    """Módulo de atención médica y citas"""
    return render_template('citas.html')

@app.route('/personal')
def personal():
    """Módulo de personal médico"""
    return render_template('personal.html')

@app.route('/experiencia')
def experiencia():
    """Módulo de experiencia médica"""
    return render_template('experiencia.html')

@app.route('/especialidad')
def especialidad():
    """Módulo de especialidades médicas"""
    return render_template('especialidad.html')

@app.route('/tipo-atencion')
def tipo_atencion():
    """Módulo de tipos de atención"""
    return render_template('tipo_atencion.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

