"""
Script para probar la nueva funcionalidad de Personal Médico
con control de rangos de ID según el nodo
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.personal_medico import PersonalMedicoModel

def test_personal_medico_ranges():
    print("=== PRUEBA DE RANGOS DE ID EN PERSONAL MÉDICO ===\n")
    
    personal_model = PersonalMedicoModel()
    
    # Test 1: Verificar detección de nodo
    print("1. VERIFICANDO DETECCIÓN DE NODO:")
    try:
        current_node = personal_model.detect_current_node()
        print(f"   Nodo detectado: {current_node}")
        
        if current_node not in ['quito', 'guayaquil']:
            print("   ❌ Nodo no válido o no detectado")
            return
        else:
            print("   ✅ Nodo detectado correctamente")
    except Exception as e:
        print(f"   ❌ Error detectando nodo: {e}")
        return
    
    # Test 2: Verificar configuración de rangos
    print("\n2. VERIFICANDO CONFIGURACIÓN DE RANGOS:")
    try:
        ranges = personal_model.ID_RANGES
        print(f"   Rangos configurados: {ranges}")
        
        if current_node in ranges:
            range_config = ranges[current_node]
            print(f"   Rango para {current_node}: {range_config['min']} - {range_config['max']}")
            print("   ✅ Configuración de rangos correcta")
        else:
            print(f"   ❌ No hay configuración de rango para {current_node}")
            return
    except Exception as e:
        print(f"   ❌ Error verificando rangos: {e}")
        return
    
    # Test 3: Verificar obtención de siguiente ID
    print("\n3. VERIFICANDO SIGUIENTE ID DISPONIBLE:")
    try:
        next_id = personal_model.get_next_available_id(current_node)
        range_config = ranges[current_node]
        
        print(f"   Siguiente ID disponible: {next_id}")
        
        if next_id is None:
            print(f"   ⚠️ No hay IDs disponibles en el rango {range_config['min']}-{range_config['max']}")
        elif range_config['min'] <= next_id <= range_config['max']:
            print(f"   ✅ ID dentro del rango válido ({range_config['min']}-{range_config['max']})")
        else:
            print(f"   ❌ ID fuera del rango válido")
            return
    except Exception as e:
        print(f"   ❌ Error obteniendo siguiente ID: {e}")
        return
    
    # Test 4: Verificar validación de rangos
    print("\n4. VERIFICANDO VALIDACIÓN DE RANGOS:")
    try:
        # Probar ID válido
        valid_id = range_config['min']
        is_valid = personal_model.validate_id_range(valid_id, current_node)
        print(f"   ID {valid_id} es válido: {is_valid}")
        
        # Probar ID inválido (fuera del rango)
        invalid_id = range_config['max'] + 5
        is_invalid = personal_model.validate_id_range(invalid_id, current_node)
        print(f"   ID {invalid_id} es válido: {is_invalid}")
        
        if is_valid and not is_invalid:
            print("   ✅ Validación de rangos funciona correctamente")
        else:
            print("   ❌ Error en validación de rangos")
    except Exception as e:
        print(f"   ❌ Error validando rangos: {e}")
        return
    
    # Test 5: Verificar lectura sin filtrado
    print("\n5. VERIFICANDO LECTURA SIN FILTRADO POR HOSPITAL:")
    try:
        result = personal_model.get_all_personal_medico(current_node)
        
        if result['success']:
            personal_data = result['personal_medico']
            print(f"   Personal médico total: {len(personal_data)} registros")
            
            # Contar por hospital
            quito_count = len([p for p in personal_data if p['ID_Hospital'] == 1])
            guayaquil_count = len([p for p in personal_data if p['ID_Hospital'] == 2])
            
            print(f"   - Hospital 1 (Quito): {quito_count} registros")
            print(f"   - Hospital 2 (Guayaquil): {guayaquil_count} registros")
            
            if quito_count > 0 and guayaquil_count > 0:
                print("   ✅ Sin filtrado - se ven ambos hospitales")
            elif quito_count > 0 or guayaquil_count > 0:
                print("   ⚠️ Solo se ve un hospital, verificar datos")
            else:
                print("   ❌ No hay datos")
        else:
            print(f"   ❌ Error al leer personal médico: {result['error']}")
    except Exception as e:
        print(f"   ❌ Error en lectura: {e}")
    
    # Test 6: Simular creación (sin insertar realmente)
    print("\n6. SIMULANDO CREACIÓN CON AUTO-ASIGNACIÓN:")
    try:
        if next_id is not None:
            hospital_id = 1 if current_node == 'quito' else 2
            
            print(f"   Se crearían con:")
            print(f"   - ID_Hospital: {hospital_id} ({current_node.capitalize()})")
            print(f"   - ID_Personal: {next_id}")
            print(f"   - Dentro del rango: {range_config['min']}-{range_config['max']}")
            print("   ✅ Auto-asignación funcionaría correctamente")
        else:
            print("   ⚠️ No se puede simular - no hay IDs disponibles")
    except Exception as e:
        print(f"   ❌ Error en simulación: {e}")
    
    print("\n=== FIN DE PRUEBAS ===")

if __name__ == "__main__":
    test_personal_medico_ranges()
