#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN RÁPIDA NODO 2 - Sistema Hospitalario
Valida que todas las funcionalidades estén operativas
"""

from models.base import DatabaseConnection
from models.personal_medico import PersonalMedicoModel
from models.especialidad import EspecialidadModel
from models.tipo_atencion import TipoAtencionModel
from models.contratos import ContratosManager
from models.pacientes import PacientesModel
from models.experiencia import ExperienciaModel
from models.atencion_medica import AtencionMedicaModel

def test_connectivity():
    """Prueba conectividad a ambos nodos"""
    print("🔗 VERIFICANDO CONECTIVIDAD...")
    
    db = DatabaseConnection()
    
    # Test Quito
    try:
        conn_quito = db.get_connection('quito')
        if conn_quito:
            conn_quito.close()
            print("✅ Conexión a Quito: OK")
        else:
            print("❌ Conexión a Quito: FALLO")
            return False
    except Exception as e:
        print(f"❌ Conexión a Quito: ERROR - {e}")
        return False
    
    # Test Guayaquil
    try:
        conn_guayaquil = db.get_connection('guayaquil')
        if conn_guayaquil:
            conn_guayaquil.close()
            print("✅ Conexión a Guayaquil: OK")
        else:
            print("❌ Conexión a Guayaquil: FALLO")
            return False
    except Exception as e:
        print(f"❌ Conexión a Guayaquil: ERROR - {e}")
        return False
    
    return True

def test_read_operations():
    """Prueba operaciones de lectura en todos los módulos"""
    print("\n📖 VERIFICANDO OPERACIONES DE LECTURA...")
    
    tests = []
    
    # Personal Médico
    try:
        pm = PersonalMedicoModel()
        result = pm.get_all_personal_medico()
        if result['success']:
            print(f"✅ Personal Médico: {result['total']} registros desde nodo {result['node']}")
            tests.append(True)
        else:
            print(f"❌ Personal Médico: {result['error']}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Personal Médico: ERROR - {e}")
        tests.append(False)
    
    # Especialidad
    try:
        esp = EspecialidadModel()
        result = esp.get_all_especialidades()
        if result['success']:
            print(f"✅ Especialidad: {result['total']} registros desde nodo {result['node']}")
            tests.append(True)
        else:
            print(f"❌ Especialidad: {result['error']}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Especialidad: ERROR - {e}")
        tests.append(False)
    
    # Tipo Atención
    try:
        ta = TipoAtencionModel()
        result = ta.get_all_tipos_atencion()
        if result['success']:
            print(f"✅ Tipo Atención: {result['total']} registros desde nodo {result['node']}")
            tests.append(True)
        else:
            print(f"❌ Tipo Atención: {result['error']}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Tipo Atención: ERROR - {e}")
        tests.append(False)
    
    # Contratos
    try:
        cm = ContratosManager()
        contratos = cm.get_all_contratos()
        print(f"✅ Contratos: {len(contratos)} registros (centralizado)")
        tests.append(True)
    except Exception as e:
        print(f"❌ Contratos: ERROR - {e}")
        tests.append(False)
    
    # Pacientes
    try:
        pac = PacientesModel()
        result = pac.get_all_pacientes()
        if result['success']:
            print(f"✅ Pacientes: {result['total']} registros desde nodo {result['node']}")
            tests.append(True)
        else:
            print(f"❌ Pacientes: {result['error']}")
            tests.append(False)
    except Exception as e:
        print(f"❌ Pacientes: ERROR - {e}")
        tests.append(False)
    
    return all(tests)

def test_node_detection():
    """Verifica detección correcta del nodo actual"""
    print("\n🌍 VERIFICANDO DETECCIÓN DE NODO...")
    
    db = DatabaseConnection()
    current_node = db.detect_current_node()
    
    if current_node == 'guayaquil':
        print("✅ Nodo detectado correctamente: GUAYAQUIL")
        return True
    elif current_node == 'quito':
        print("⚠️ Nodo detectado: QUITO (verificar configuración si estás en Guayaquil)")
        return True
    else:
        print(f"❌ Error en detección de nodo: {current_node}")
        return False

def test_write_restrictions():
    """Verifica restricciones de escritura"""
    print("\n🔒 VERIFICANDO RESTRICCIONES DE ESCRITURA...")
    
    # Tipo Atención (debe estar restringido en Guayaquil)
    try:
        ta = TipoAtencionModel()
        current_node = ta.detect_current_node()
        
        if current_node == 'guayaquil':
            # Intentar crear (debe fallar)
            result = ta.create_tipo_atencion({'Tipo': 'Test'})
            if not result['success'] and 'Solo permitido en nodo Quito' in result['error']:
                print("✅ Tipo Atención: Restricción funcionando correctamente")
                return True
            else:
                print("❌ Tipo Atención: Restricción NO funcionando")
                return False
        else:
            print("ℹ️ Tipo Atención: Nodo Quito detectado, restricciones no aplican")
            return True
    except Exception as e:
        print(f"❌ Error probando restricciones: {e}")
        return False

def main():
    """Ejecuta todas las verificaciones"""
    print("🚀 VERIFICACIÓN RÁPIDA NODO 2 - SISTEMA HOSPITALARIO")
    print("=" * 60)
    
    results = []
    
    # 1. Conectividad
    results.append(test_connectivity())
    
    # 2. Detección de nodo
    results.append(test_node_detection())
    
    # 3. Operaciones de lectura
    results.append(test_read_operations())
    
    # 4. Restricciones de escritura
    results.append(test_write_restrictions())
    
    print("\n" + "=" * 60)
    
    if all(results):
        print("🎊 ¡VERIFICACIÓN COMPLETA EXITOSA!")
        print("✅ El Nodo 2 está listo para usar")
        print("\n🌐 Iniciar aplicación: python app.py")
        print("🔗 URL: http://localhost:5000")
    else:
        print("⚠️ VERIFICACIÓN CON ERRORES")
        print("❌ Revisar configuración antes de usar")
        
        print("\n🔧 PASOS DE SOLUCIÓN:")
        print("1. Verificar archivo .env")
        print("2. Comprobar SQL Server está corriendo")
        print("3. Validar conectividad de red")
        print("4. Revisar credenciales de base de datos")

if __name__ == "__main__":
    main()
