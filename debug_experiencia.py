
from models.experiencia import ExperienciaModel

def debug_experiencia():
    model = ExperienciaModel()
    print("\n1️⃣ CREANDO EXPERIENCIA DE PRUEBA")
    print("-" * 35)
    experiencia_data = {
        'Cargo': 'Cardiólogo',
        'Anios_exp': 5,
        'auto_id': True
    }
    create_result = model.create_experiencia(experiencia_data)
    print(create_result)

    if create_result['success']:
        id_personal = create_result['id_personal']
        id_hospital = create_result['id_hospital']

        # Verificar creación (buscar por ID)
        print("\n2️⃣ VERIFICANDO CREACIÓN")
        print("-" * 35)
        experiencia = model.get_experiencia_by_id(id_hospital, id_personal)
        if experiencia:
            print(f"✅ Experiencia creada: {experiencia}")
        else:
            print("❌ No se encontró la experiencia creada")

        # Actualizar experiencia
        print("\n3️⃣ ACTUALIZANDO EXPERIENCIA")
        print("-" * 35)
        update_result = model.update_experiencia(id_hospital, id_personal, {'Cargo': 'Cardiólogo', 'Anios_exp': 6})
        print(update_result)

        # Verificar actualización
        print("\n4️⃣ VERIFICANDO ACTUALIZACIÓN")
        print("-" * 35)
        experiencia_mod = model.get_experiencia_by_id(id_hospital, id_personal)
        if experiencia_mod:
            print(f"✅ Experiencia actualizada: {experiencia_mod}")
        else:
            print("❌ No se encontró la experiencia actualizada")

        # Buscar experiencia por cargo
        print("\n5️⃣ PROBANDO BÚSQUEDA POR CARGO")
        print("-" * 35)
        search_result = model.search_experiencias('Cardiólogo')
        if search_result['success']:
            print(f"🔍 Búsqueda exitosa: {search_result['total']} resultados encontrados")
            for exp in search_result.get('experiencias', []):
                print(f"   🔸 {exp}")
        else:
            print(f"❌ Error en búsqueda: {search_result['error']}")

        # Eliminar experiencia
        print("\n6️⃣ ELIMINANDO EXPERIENCIA DE PRUEBA")
        print("-" * 35)
        delete_result = model.delete_experiencia(id_hospital, id_personal, 'Cardiólogo')
        print(delete_result)

        # Verificar eliminación
        experiencia_del = model.get_experiencia_by_id(id_hospital, id_personal)
        if not experiencia_del:
            print("✅ Verificación: Experiencia eliminada correctamente")
        else:
            print("⚠️ Advertencia: La experiencia aún existe después de la eliminación")
    else:
        print(f"❌ Error creando experiencia: {create_result['error']}")

if __name__ == "__main__":
    debug_experiencia()
