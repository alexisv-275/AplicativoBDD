# Sistema Hospitalario Distribuido 🏥

Aplicación Flask para gestión de pacientes con base de datos distribuida entre Quito y Guayaquil.

## 🚀 Configuración del Entorno (OBLIGATORIO)

### Para Windows:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/alexisv-275/AplicativoBDD.git
   cd AplicativoBDD
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv .venv
   ```

3. **Activar entorno virtual:**
   ```bash
   .\.venv\Scripts\activate
   ```

   **Desactivar entorno virtual:**
   deactivate
   ✅ Deberías ver `(.venv)` al inicio de tu terminal

4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar VS Code:**
   - Presiona `Ctrl + Shift + P`
   - Escribe `Python: Select Interpreter`
   - Selecciona `./.venv/Scripts/python.exe`

### Para Linux/Mac:

1. **Clonar y navegar:**
   ```bash
   git clone https://github.com/alexisv-275/AplicativoBDD.git
   cd AplicativoBDD
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración de Base de Datos

1. **Copiar archivo de configuración:**
   ```bash
   cp .env.example .env
   ```

2. **Editar `.env` con tus credenciales de SQL Server:**
   ```env
   # Nodo Quito
   DB_QUITO_SERVER=localhost
   DB_QUITO_DATABASE=Hospital_Quito
   DB_QUITO_USERNAME=tu_usuario
   DB_QUITO_PASSWORD=tu_password

   # Nodo Guayaquil  
   DB_GUAYAQUIL_SERVER=localhost
   DB_GUAYAQUIL_DATABASE=Hospital_Guayaquil
   DB_GUAYAQUIL_USERNAME=tu_usuario
   DB_GUAYAQUIL_PASSWORD=tu_password
   ```

## 🏃‍♂️ Ejecutar la Aplicación

```bash
# Asegúrate de que el entorno virtual está activado
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🛠️ Tecnologías

- **Backend:** Flask 3.1.1
- **Base de Datos:** SQL Server con PyODBC 5.2.0
- **Frontend:** Bootstrap 5 + JavaScript
- **Entorno:** Python 3.13

## 📁 Estructura del Proyecto

```
AplicativoBDD/
├── .venv/              # Entorno virtual (NO incluir en Git)
├── static/             # CSS, JS, imágenes
├── templates/          # Plantillas HTML
├── app.py             # Aplicación principal
├── database.py        # Conexiones de BD
├── .env              # Configuración (NO incluir en Git)
└── requirements.txt   # Dependencias
```

## ❗ Problemas Comunes

**"ModuleNotFoundError: No module named 'flask'"**
- Solución: Activa el entorno virtual con `.\.venv\Scripts\activate`

**VS Code no reconoce los imports:**
- Solución: `Ctrl + Shift + P` → `Python: Select Interpreter` → `./.venv/Scripts/python.exe`

**Error de conexión a base de datos:**
- Verifica que SQL Server esté corriendo
- Revisa las credenciales en `.env`