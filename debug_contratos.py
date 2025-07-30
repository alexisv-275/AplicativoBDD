"""
Script para debuggear el problema de inserción en Contratos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.contratos import ContratosManager

def test_contrato_insertion():
    print("=== PRUEBA DE INSERCIÓN DE CONTRATOS ===\n")
    
    contratos_manager = ContratosManager()
    
    # Test 1: Verificar conexión básica
    print("1. VERIFICANDO CONEXIÓN BÁSICA:")
    try:
        current_node = contratos_manager.detect_current_node()
        print(f"   Nodo detectado: {current_node}")
        
        if current_node:
            connection = contratos_manager.get_connection()
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
    print("\n2. VERIFICANDO LECTURA DE DATOS:")
    try:
        contratos_existentes = contratos_manager.get_all_contratos()
        print(f"   Contratos existentes: {len(contratos_existentes)}")
        
        if contratos_existentes:
            print(f"   Primer contrato: Hospital {contratos_existentes[0]['ID_Hospital']}, Personal {contratos_existentes[0]['ID_Personal']}")
    except Exception as e:
        print(f"   ❌ Error al leer contratos: {e}")
        return
    
    # Test 3: Intentar inserción simple
    print("\n3. INTENTANDO INSERCIÓN CON STORED PROCEDURE:")
    try:
        # Usar datos de prueba que deberían funcionar
        test_hospital_id = 1  # Quito
        test_personal_id = 998  # ID que probablemente no existe
        test_salario = 2800.00
        
        print(f"   Intentando insertar con SP: Hospital {test_hospital_id}, Personal {test_personal_id}, Salario ${test_salario}")
        
        # Intentar inserción con SP
        result = contratos_manager.create_contrato(test_hospital_id, test_personal_id, test_salario)
        
        if result:
            print("   ✅ Inserción con SP exitosa!")
            
            # Verificar que se insertó
            nuevo_contrato = contratos_manager.get_contrato_by_ids(test_hospital_id, test_personal_id)
            if nuevo_contrato:
                print(f"   ✅ Contrato confirmado en BD: Salario ${nuevo_contrato['Salario']}")
                
                # Limpiar - eliminar el contrato de prueba
                contratos_manager.delete_contrato(test_hospital_id, test_personal_id)
                print("   🧹 Contrato de prueba eliminado")
            else:
                print("   ⚠️ Contrato no encontrado después de inserción")
        else:
            print("   ❌ Inserción con SP falló")
            
    except Exception as e:
        print(f"   ❌ Error durante inserción con SP: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Probar con fecha
    print("\n4. INTENTANDO INSERCIÓN CON STORED PROCEDURE Y FECHA:")
    try:
        from datetime import date
        
        test_hospital_id = 2  # Guayaquil
        test_personal_id = 997  # ID que probablemente no existe
        test_salario = 3200.00
        test_fecha = date.today()
        
        print(f"   Intentando insertar con SP y fecha: Hospital {test_hospital_id}, Personal {test_personal_id}, Salario ${test_salario}, Fecha {test_fecha}")
        
        # Intentar inserción con SP y fecha
        result = contratos_manager.create_contrato(test_hospital_id, test_personal_id, test_salario, test_fecha)
        
        if result:
            print("   ✅ Inserción con SP y fecha exitosa!")
            
            # Verificar que se insertó
            nuevo_contrato = contratos_manager.get_contrato_by_ids(test_hospital_id, test_personal_id)
            if nuevo_contrato:
                print(f"   ✅ Contrato confirmado: Salario ${nuevo_contrato['Salario']}, Fecha {nuevo_contrato['Fecha_Contrato']}")
                
                # Limpiar - eliminar el contrato de prueba
                contratos_manager.delete_contrato(test_hospital_id, test_personal_id)
                print("   🧹 Contrato de prueba eliminado")
            else:
                print("   ⚠️ Contrato no encontrado después de inserción")
        else:
            print("   ❌ Inserción con SP y fecha falló")
            
    except Exception as e:
        print(f"   ❌ Error durante inserción con SP y fecha: {e}")
        import traceback
        traceback.print_exc()
            
    except Exception as e:
        print(f"   ❌ Error durante inserción: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIN DE PRUEBAS ===")

if __name__ == "__main__":
    test_contrato_insertion()
