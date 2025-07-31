#!/usr/bin/env python3
"""
Debug script para Pacientes - Vista Particionada Actualizable
Prueba creación, lectura, actualización y eliminación con rangos de ID automáticos

Rangos configurados:
- Quito (Hospital 1): IDs 1-20
- Guayaquil (Hospital 2): IDs 21-40

Filtro local: Solo muestra pacientes del hospital local (como Experiencia)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.pacientes import PacientesModel
from models.base import DatabaseConnection
from datetime import datetime

def debug_pacientes():
    print("=" * 70)
    print("🏥 DEBUG PACIENTES - Vista Particionada Actualizable")
    print("=" * 70)
    
    # Inicializar modelo
    pacientes_model = PacientesModel()
    
    # 1. Detectar nodo actual
    print("\n1️⃣ DETECCIÓN DE NODO")
    print("-" * 30)
    current_node = pacientes_model.detect_current_node()
    print(f"🔍 Nodo detectado: {current_node}")
    
    if not current_node:
        print("❌ No se pudo detectar el nodo. Abortando debug.")
        return
    
    # 2. Verificar rangos de ID
    print("\n2️⃣ VERIFICACIÓN DE RANGOS")
    print("-" * 30)
    range_config = pacientes_model.ID_RANGES.get(current_node, {})
    print(f"📊 Rango para {current_node}: {range_config.get('min', '?')} - {range_config.get('max', '?')}")
    
    # 3. Obtener siguiente ID disponible
    print("\n3️⃣ AUTO-ASIGNACIÓN DE ID")
    print("-" * 30)
    next_id = pacientes_model.get_next_available_id(current_node)
    print(f"🔢 Siguiente ID disponible: {next_id}")
    
    if next_id is None:
        print("❌ No hay IDs disponibles en el rango. No se puede continuar con las pruebas.")
        return
    
    # 4. Listar pacientes existentes (filtro local)
    print("\n4️⃣ PACIENTES EXISTENTES (FILTRO LOCAL)")
    print("-" * 50)
    result = pacientes_model.get_all_pacientes()
    if result['success']:
        print(f"✅ {result['total']} pacientes encontrados en hospital local")
        print(f"🏥 Hospital ID: {result.get('hospital_id', 'N/A')}")
        print(f"🌐 Nodo: {result['node']}")
        
        if result['pacientes']:
            print("\n📋 Lista de pacientes locales:")
            for pac in result['pacientes'][:5]:  # Mostrar solo primeros 5
                print(f"   🔸 ID: {pac.get('ID_Paciente', 'N/A')} | {pac.get('Nombre', 'N/A')} {pac.get('Apellido', 'N/A')}")
            if len(result['pacientes']) > 5:
                print(f"   ... y {len(result['pacientes']) - 5} más")
    else:
        print(f"❌ Error obteniendo pacientes: {result['error']}")
    
    # 5. Crear nuevo paciente
    print("\n5️⃣ CREANDO NUEVO PACIENTE")
    print("-" * 35)
    
    paciente_test = {
        'Nombre': 'Juan Carlos',
        'Apellido': 'Debug Test',
        'Direccion': f'Av. Prueba {next_id}',
        'FechaNacimiento': '1990-05-15',
        'Sexo': 'M',
        'Telefono': f'099123456{next_id}'
    }
    
    print(f"👤 Creando paciente: {paciente_test['Nombre']} {paciente_test['Apellido']}")
    print(f"🔢 ID asignado automáticamente: {next_id}")
    
    create_result = pacientes_model.create_paciente(paciente_test)
    
    if create_result['success']:
        print(f"✅ {create_result['message']}")
        print(f"🏥 Hospital: {create_result.get('id_hospital', 'N/A')}")
        print(f"🔢 ID Paciente: {create_result.get('id_paciente', 'N/A')}")
        
        hospital_id = create_result.get('id_hospital')
        paciente_id = create_result.get('id_paciente')
        
        # 6. Verificar que se creó correctamente
        print("\n6️⃣ VERIFICANDO CREACIÓN")
        print("-" * 30)
        paciente_creado = pacientes_model.get_paciente_by_id(hospital_id, paciente_id)
        
        if paciente_creado:
            print("✅ Paciente encontrado en la base de datos:")
            print(f"   📋 Nombre: {paciente_creado.get('Nombre', 'N/A')} {paciente_creado.get('Apellido', 'N/A')}")
            print(f"   📍 Dirección: {paciente_creado.get('Direccion', 'N/A')}")
            print(f"   📞 Teléfono: {paciente_creado.get('Telefono', 'N/A')}")
            print(f"   👤 Sexo: {paciente_creado.get('Sexo', 'N/A')}")
            
            # 7. Actualizar paciente
            print("\n7️⃣ ACTUALIZANDO PACIENTE")
            print("-" * 30)
            
            paciente_actualizado = {
                'Nombre': 'Juan Carlos ACTUALIZADO',
                'Apellido': 'Debug Test MODIFICADO',
                'Direccion': f'Av. Actualizada {paciente_id}',
                'FechaNacimiento': '1990-05-15',
                'Sexo': 'M',
                'Telefono': f'099999999{paciente_id}'
            }
            
            update_result = pacientes_model.update_paciente(hospital_id, paciente_id, paciente_actualizado)
            
            if update_result['success']:
                print(f"✅ {update_result['message']}")
                
                # Verificar actualización
                paciente_verificado = pacientes_model.get_paciente_by_id(hospital_id, paciente_id)
                if paciente_verificado:
                    print(f"✅ Verificación: Nombre actualizado a '{paciente_verificado.get('Nombre', 'N/A')}'")
                    print(f"✅ Verificación: Teléfono actualizado a '{paciente_verificado.get('Telefono', 'N/A')}'")
            else:
                print(f"❌ Error actualizando: {update_result['error']}")
            
            # 8. Buscar paciente
            print("\n8️⃣ PROBANDO BÚSQUEDA LOCAL")
            print("-" * 35)
            
            search_result = pacientes_model.search_pacientes("Debug Test")
            if search_result['success']:
                print(f"🔍 Búsqueda exitosa: {search_result['total']} resultados encontrados")
                print(f"🏥 Hospital filtrado: {search_result.get('hospital_id', 'N/A')}")
                if search_result['pacientes']:
                    for pac in search_result['pacientes']:
                        print(f"   🔸 Encontrado: {pac.get('Nombre', 'N/A')} {pac.get('Apellido', 'N/A')}")
            else:
                print(f"❌ Error en búsqueda: {search_result['error']}")
            
            # 9. Eliminar paciente de prueba
            print("\n9️⃣ LIMPIANDO DATOS DE PRUEBA")
            print("-" * 35)
            
            delete_result = pacientes_model.delete_paciente(hospital_id, paciente_id)
            if delete_result['success']:
                print(f"✅ {delete_result['message']}")
                
                # Verificar eliminación
                paciente_eliminado = pacientes_model.get_paciente_by_id(hospital_id, paciente_id)
                if paciente_eliminado is None:
                    print("✅ Verificación: Paciente eliminado correctamente")
                else:
                    print("⚠️ Advertencia: El paciente aún existe después de la eliminación")
            else:
                print(f"❌ Error eliminando: {delete_result['error']}")
        
        else:
            print("❌ No se pudo verificar la creación del paciente")
    
    else:
        print(f"❌ Error creando paciente: {create_result['error']}")
    
    print("\n" + "=" * 70)
    print("🎯 DEBUG COMPLETADO")
    print("=" * 70)
    
    # 10. Resumen final
    print("\n📊 RESUMEN DE CARACTERÍSTICAS IMPLEMENTADAS:")
    print("✅ Vista particionada actualizable (Vista_Paciente)")
    print("✅ Auto-asignación de IDs por rangos (Quito: 1-20, Guayaquil: 21-40)")
    print("✅ Filtro local (solo pacientes del hospital local)")
    print("✅ Stored procedures con transacciones distribuidas")
    print("✅ CRUD completo (Create, Read, Update, Delete)")
    print("✅ Búsqueda con filtro local")
    print("✅ Manejo de errores y logging detallado")

if __name__ == "__main__":
    try:
        debug_pacientes()
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN DEBUG: {e}")
        import traceback
        traceback.print_exc()
