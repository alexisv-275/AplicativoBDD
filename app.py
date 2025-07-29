from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import DatabaseConnection
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Instancia de la conexión a la base de datos
db = DatabaseConnection()

@app.route('/')
def index():
    """Página principal del sistema hospitalario"""
    return render_template('index.html')

@app.route('/pacientes')
def listar_pacientes():
    """Lista todos los pacientes de ambos nodos"""
    try:
        # Consulta a la vista distribuida de pacientes
        query = "SELECT * FROM VistaPacientes"
        pacientes = db.execute_query(query, node='quito')  # Usar la vista desde cualquier nodo
        
        return render_template('pacientes/lista.html', pacientes=pacientes)
    except Exception as e:
        flash(f'Error al cargar pacientes: {str(e)}', 'error')
        return render_template('pacientes/lista.html', pacientes=[])

@app.route('/pacientes/nuevo', methods=['GET', 'POST'])
def nuevo_paciente():
    """Crear un nuevo paciente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cedula = request.form['cedula']
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            fecha_nacimiento = request.form['fecha_nacimiento']
            telefono = request.form['telefono']
            email = request.form['email']
            direccion = request.form['direccion']
            ciudad = request.form['ciudad']
            
            # Insertar en la vista (se dirigirá automáticamente al nodo correcto por la fragmentación)
            query = """
                INSERT INTO VistaPacientes 
                (cedula, nombres, apellidos, fecha_nacimiento, telefono, email, direccion, ciudad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (cedula, nombres, apellidos, fecha_nacimiento, telefono, email, direccion, ciudad)
            
            result = db.execute_query(query, params, 'quito')  # La vista manejará la fragmentación
            
            if result is not None:
                flash('Paciente creado exitosamente', 'success')
                return redirect(url_for('listar_pacientes'))
            else:
                flash('Error al crear el paciente', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('pacientes/nuevo.html')

@app.route('/pacientes/editar/<cedula>', methods=['GET', 'POST'])
def editar_paciente(cedula):
    """Editar un paciente existente"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            fecha_nacimiento = request.form['fecha_nacimiento']
            telefono = request.form['telefono']
            email = request.form['email']
            direccion = request.form['direccion']
            ciudad = request.form['ciudad']
            
            # Actualizar en la vista
            query = """
                UPDATE VistaPacientes 
                SET nombres=?, apellidos=?, fecha_nacimiento=?, telefono=?, email=?, direccion=?, ciudad=?
                WHERE cedula=?
            """
            params = (nombres, apellidos, fecha_nacimiento, telefono, email, direccion, ciudad, cedula)
            
            result = db.execute_query(query, params, 'quito')
            
            if result is not None and result > 0:
                flash('Paciente actualizado exitosamente', 'success')
                return redirect(url_for('listar_pacientes'))
            else:
                flash('Error al actualizar el paciente', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # Obtener datos del paciente para el formulario
    try:
        query = "SELECT * FROM VistaPacientes WHERE cedula = ?"
        paciente = db.execute_query(query, (cedula,), 'quito')
        if paciente:
            paciente = paciente[0]  # Primer resultado
            return render_template('pacientes/editar.html', paciente=paciente)
        else:
            flash('Paciente no encontrado', 'error')
            return redirect(url_for('listar_pacientes'))
    except Exception as e:
        flash(f'Error al cargar paciente: {str(e)}', 'error')
        return redirect(url_for('listar_pacientes'))

@app.route('/pacientes/eliminar/<cedula>', methods=['POST'])
def eliminar_paciente(cedula):
    """Eliminar un paciente"""
    try:
        query = "DELETE FROM VistaPacientes WHERE cedula = ?"
        result = db.execute_query(query, (cedula,), 'quito')
        
        if result is not None and result > 0:
            flash('Paciente eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar el paciente', 'error')
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('listar_pacientes'))

@app.route('/estadisticas')
def estadisticas():
    """Mostrar estadísticas del sistema distribuido"""
    try:
        # Consultas para estadísticas
        query_total_pacientes = "SELECT COUNT(*) as total FROM VistaPacientes"
        query_pacientes_quito = "SELECT COUNT(*) as total FROM PacientesQuito"
        query_pacientes_guayaquil = "SELECT COUNT(*) as total FROM PacientesGuayaquil"
        
        total_pacientes = db.execute_query(query_total_pacientes, node='quito')[0][0]
        pacientes_quito = db.execute_query(query_pacientes_quito, node='quito')[0][0]
        pacientes_guayaquil = db.execute_query(query_pacientes_guayaquil, node='guayaquil')[0][0]
        
        stats = {
            'total_pacientes': total_pacientes,
            'pacientes_quito': pacientes_quito,
            'pacientes_guayaquil': pacientes_guayaquil
        }
        
        return render_template('estadisticas.html', stats=stats)
        
    except Exception as e:
        flash(f'Error al cargar estadísticas: {str(e)}', 'error')
        return render_template('estadisticas.html', stats={})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
