from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import DatabaseConnection
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

# Instancia de la conexión a la base de datos
db = DatabaseConnection()

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
    """Módulo de gestión de pacientes"""
    return render_template('pacientes.html')

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

