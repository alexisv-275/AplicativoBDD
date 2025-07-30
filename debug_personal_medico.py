"""
Script para debuggear el nuevo SP de Personal Médico + Contratos
Prueba la creación simultánea en Vista_INF_Personal y Contratos
"""
import sys
import os
from datetime import date

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.personal_medico import PersonalMedicoModel
from models.contratos import ContratosManager

def test_personal_medico_with_contratos():
    print("=== PRUEBA FUNCIONAL DE PERSONAL MÉDICO + CONTRATOS ===\n")
    
    personal_model = PersonalMedicoModel()
    contratos_manager = ContratosManager()
    
    # Test 1: Verificar conexión básica
    print("1. VERIFICANDO CONEXIÓN BÁSICA:")
    try:
        current_node = personal_model.detect_current_node()
        print(f"   Nodo detectado: {current_node}")
        
        if current_node:
            connection = personal_model.get_connection()
            if connection:
                print("   ✅ Conexión establecida correctamente")
                connection.close()
            else:
                print("   ❌ Error al establecer conexión")
                return
        else:
            print("   ❌ No se pudo detectar ningún nodo")
            return
    except Exception as e:
        print(f"   ❌ Error en conexión básica: {e}")
        return
    
    # Test 2: Verificar lectura de datos existentes
    print("\n2. VERIFICANDO LECTURA DE DATOS EXISTENTES:")
    try:
        # Personal médico existente
        personal_result = personal_model.get_all_personal_medico(current_node)
        if personal_result['success']:
            personal_count = len(personal_result['personal_medico'])
            print(f"   Personal médico existente: {personal_count} registros")
            if personal_count > 0:
                primer_personal = personal_result['personal_medico'][0]
                print(f"   Primer registro: Hospital {primer_personal['ID_Hospital']}, Personal {primer_personal['ID_Personal']}")
        else:
            print(f"   ❌ Error leyendo personal médico: {personal_result['error']}")
            return
        
        # Contratos existentes
        contratos_existentes = contratos_manager.get_all_contratos()
        print(f"   Contratos existentes: {len(contratos_existentes)}")
        
    except Exception as e:
        print(f"   ❌ Error al leer datos existentes: {e}")
        return
    
    # Test 3: Obtener siguiente ID disponible
    print("\n3. OBTENIENDO SIGUIENTE ID DISPONIBLE:")
    try:
        next_id = personal_model.get_next_available_id(current_node)
        if next_id is None:
            print(f"   ❌ No hay IDs disponibles en el rango para {current_node}")
            return
        else:
            print(f"   ✅ Siguiente ID disponible: {next_id}")
            
        hospital_id = 1 if current_node == 'quito' else 2
        print(f"   Hospital correspondiente: {hospital_id}")
        
    except Exception as e:
        print(f"   ❌ Error obteniendo siguiente ID: {e}")
        return
    
    # Test 4: Probar creación REAL con SP integrado
    print("\n4. PROBANDO CREACIÓN CON SP INTEGRADO (PERSONAL + CONTRATO):")
    try:
        test_data = {
            'ID_Especialidad': 1,
            'Nombre': 'Dr. Test',
            'Apellido': 'Debug',
            'Teléfono': '0999123456'
        }
        test_salario = 3500.00
        test_fecha = date.today()
        
        print(f"   Intentando crear con SP integrado: Hospital {hospital_id}, Personal {next_id}")
        print(f"   Datos: {test_data['Nombre']} {test_data['Apellido']}, Esp: {test_data['ID_Especialidad']}, Salario: ${test_salario}")
        
        # Crear personal médico + contrato con SP integrado
        result = personal_model.create_personal_medico_with_contrato(test_data, test_salario, test_fecha, current_node)
        
        if result['success']:
            print("   ✅ Personal médico + contrato creados exitosamente!")
            print(f"   ID asignado: Hospital {result.get('id_hospital', '?')}, Personal {result.get('id_personal', '?')}")
            
            # Test 5: Verificar que se crearon ambos registros
            print("\n5. VERIFICANDO CREACIÓN EN AMBAS TABLAS:")
            
            # Verificar personal médico
            personal_result = personal_model.get_all_personal_medico(current_node)
            personal_creado = None
            if personal_result['success']:
                personal_data = personal_result['personal_medico']
                personal_creado = next((p for p in personal_data 
                                     if p['ID_Hospital'] == result.get('id_hospital') 
                                     and p['ID_Personal'] == result.get('id_personal')), None)
            
            if personal_creado:
                print(f"   ✅ Personal confirmado en Vista_INF_Personal: {personal_creado['Nombre']} {personal_creado['Apellido']}")
            else:
                print("   ❌ Personal NO encontrado en Vista_INF_Personal")
            
            # Verificar contrato
            contrato_creado = contratos_manager.get_contrato_by_ids(
                result.get('id_hospital'), 
                result.get('id_personal')
            )
            
            if contrato_creado:
                print(f"   ✅ Contrato confirmado en tabla Contratos: Salario ${contrato_creado['Salario']}, Fecha {contrato_creado['Fecha_Contrato']}")
            else:
                print("   ❌ Contrato NO encontrado en tabla Contratos")
            
            # Test 6: Limpiar datos de prueba
            print("\n6. LIMPIANDO DATOS DE PRUEBA:")
            
            if personal_creado and contrato_creado:
                # Eliminar contrato primero
                delete_contrato = contratos_manager.delete_contrato(
                    result.get('id_hospital'), 
                    result.get('id_personal')
                )
                
                if delete_contrato:
                    print("   ✅ Contrato eliminado")
                else:
                    print("   ⚠️ Error eliminando contrato")
                
                # Eliminar personal médico
                delete_personal = personal_model.delete_personal_medico(
                    result.get('id_hospital'), 
                    result.get('id_personal'), 
                    current_node
                )
                
                if delete_personal['success']:
                    print("   ✅ Personal médico eliminado")
                else:
                    print(f"   ⚠️ Error eliminando personal: {delete_personal['error']}")
                    
                print("   🧹 Limpieza completada")
            else:
                print("   ⚠️ Limpieza omitida - algún registro no se encontró")
                
        else:
            print(f"   ❌ Error creando con SP integrado: {result['error']}")
            
    except Exception as e:
        print(f"   ❌ Error durante prueba de SP integrado: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Información sobre próxima implementación
    print("\n7. PRÓXIMA IMPLEMENTACIÓN CON SP INTEGRADO:")
    print("   🔄 Cuando esté listo el SP_Create_PersonalMedico:")
    print("   - Creará personal + contrato en una sola transacción")
    print("   - Usará BEGIN DISTRIBUTED TRANSACTION")
    print("   - Validará duplicados automáticamente")
    print("   - Manejo de errores robusto")
    
    # Test 8: Verificar rangos de ID
    print("\n8. VERIFICANDO RANGOS DE ID:")
    try:
        ranges = personal_model.ID_RANGES
        current_range = ranges.get(current_node, {})
        print(f"   Rango para {current_node}: {current_range.get('min', '?')} - {current_range.get('max', '?')}")
        
        # Contar IDs usados en el rango
        personal_result = personal_model.get_all_personal_medico(current_node)
        if personal_result['success']:
            personal_data = personal_result['personal_medico']
            hospital_filter = 1 if current_node == 'quito' else 2
            
            ids_usados = [p['ID_Personal'] for p in personal_data 
                         if p['ID_Hospital'] == hospital_filter 
                         and current_range.get('min', 0) <= p['ID_Personal'] <= current_range.get('max', 0)]
            
            ids_usados.sort()
            print(f"   IDs usados en {current_node}: {ids_usados}")
            print(f"   IDs disponibles: {current_range.get('max', 0) - len(ids_usados)}")
            
    except Exception as e:
        print(f"   ❌ Error verificando rangos: {e}")
    
    print("\n=== FIN DE PRUEBAS FUNCIONALES ===")

if __name__ == "__main__":
    test_personal_medico_with_contratos()
