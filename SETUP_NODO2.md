# 🚀 CONFIGURACIÓN NODO 2 (GUAYAQUIL) - SETUP RÁPIDO

## 📋 PASOS OBLIGATORIOS

### 1. 📥 Clonar Repositorio
```bash
git clone https://github.com/alexisv-275/AplicativoBDD.git
cd AplicativoBDD
```

### 2. 🐍 Entorno Python
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. ⚙️ CONFIGURAR .env (CRÍTICO)
Crear archivo `.env` con estos valores EXACTOS:

```properties
# Configuración de Base de Datos Distribuida - Sistema Hospitalario

# Nodo Quito (REMOTO)
DB_QUITO_SERVER=ASUSVIVOBOOK
DB_QUITO_DATABASE=Red_de_salud_Quito
DB_QUITO_USERNAME=sa
DB_QUITO_PASSWORD=password123

# Nodo Guayaquil (LOCAL)
DB_GUAYAQUIL_SERVER=TU_SERVIDOR_LOCAL
DB_GUAYAQUIL_DATABASE=R_RedSalud
DB_GUAYAQUIL_USERNAME=sa
DB_GUAYAQUIL_PASSWORD=TU_PASSWORD

# Configuración Flask
FLASK_ENV=development
SECRET_KEY=mi_proyecto_hospital_2025_desarrollo_local
DEBUG=True
```

**🚨 CAMBIAR ESTOS VALORES:**
- `DB_GUAYAQUIL_SERVER`: Nombre de tu servidor SQL Server local
- `DB_GUAYAQUIL_PASSWORD`: Tu contraseña de SQL Server

### 4. 🗄️ Verificar Conectividad de Base de Datos
```bash
python test_connection.py
```

**Debe mostrar:**
```
✅ Conexión exitosa a quito
✅ Conexión exitosa a guayaquil
```

### 5. 🚀 Ejecutar Aplicación
```bash
python app.py
```

**URL:** http://localhost:5000

---

## 🔍 VERIFICACIÓN RÁPIDA

### ✅ Funcionalidades que DEBEN funcionar en Nodo 2:

#### **📊 LECTURA (Todos los módulos):**
- ✅ **Personal Médico**: Lee desde Vista_INF_Personal local
- ✅ **Especialidad**: Lee desde tabla replicada
- ✅ **Tipo Atención**: Lee desde tabla replicada  
- ✅ **Contratos**: Lee desde Quito (centralizado)
- ✅ **Experiencia**: Lee con filtro hospital=2
- ✅ **Atención Médica**: Lee con filtro hospital=2
- ✅ **Pacientes**: Lee con filtro hospital=2

#### **✏️ ESCRITURA PERMITIDA:**
- ✅ **Personal Médico**: CREATE/UPDATE/DELETE con SPs distribuidos
- ✅ **Especialidad**: CREATE/UPDATE/DELETE (replicación bidireccional)
- ✅ **Experiencia**: CREATE/UPDATE/DELETE (filtrado por hospital=2)
- ✅ **Atención Médica**: CREATE/UPDATE/DELETE (filtrado por hospital=2)  
- ✅ **Pacientes**: CREATE/UPDATE/DELETE (filtrado por hospital=2)

#### **🔒 ESCRITURA RESTRINGIDA:**
- ❌ **Tipo Atención**: Solo lectura (replicación unidireccional desde Quito)
- ➡️ **Contratos**: Manejo centralizado desde Quito

---

## 🐛 TROUBLESHOOTING COMÚN

### **Error de Conexión a Base de Datos:**
```
Error: No se puede conectar a ningún nodo
```
**Solución:** Verificar `.env` y conectividad SQL Server

### **Error de Personal Médico:**
```
Error en SP_Create_PersonalMedico
```
**Solución:** Verificar que existan los SPs en la base de datos

### **Error de Tipo Atención:**
```
Solo permitido en nodo Quito (Master)
```
**Solución:** ✅ COMPORTAMIENTO CORRECTO - Tipo Atención es read-only en Guayaquil

### **Error de Contratos:**
```
Error al consultar Contratos
```
**Solución:** Verificar conectividad con nodo Quito (centralizado)

---

## 📞 CONTACTO SOPORTE

Si hay problemas, verificar:
1. ✅ Archivo `.env` configurado correctamente
2. ✅ SQL Server corriendo y accesible
3. ✅ Dependencias Python instaladas
4. ✅ Puertos de red abiertos entre nodos

**🎯 Con esta configuración, el Nodo 2 debería funcionar inmediatamente.**
