from models.atencion_medica import AtencionMedicaModel
from datetime import date

# Instanciar el modelo
model = AtencionMedicaModel()

# Nodo de prueba (puedes cambiar a 'guayaquil' para probar el otro rango)
node = 'quito'

print('--- TEST: Obtener siguiente ID disponible ---')
next_id = model.get_next_available_id(node)
print('Siguiente ID disponible:', next_id)

print('\n--- TEST: Crear atención médica ---')
create_data = {
    'ID_Personal': 1,
    'ID_Paciente': 1,
    'ID_Tipo': 1,
    'Fecha': date.today().isoformat(),
    'Diagnostico': 'Prueba Diagnóstico',
    'Descripción': 'Prueba Descripción',
    'Tratamiento': 'Prueba Tratamiento'
}
result_create = model.create_atencion_medica(create_data, node=node)
print('Resultado creación:', result_create)

if result_create.get('id_atencion'):
    id_atencion = result_create['id_atencion']
else:
    id_atencion = next_id

print('\n--- TEST: Actualizar atención médica ---')
update_data = create_data.copy()
update_data['Diagnostico'] = 'Diagnóstico actualizado'
update_data['Descripción'] = 'Descripción actualizada'
update_data['Tratamiento'] = 'Tratamiento actualizado'
result_update = model.update_atencion_medica(1 if node == 'quito' else 2, id_atencion, update_data, node=node)
print('Resultado actualización:', result_update)

print('\n--- TEST: Eliminar atención médica ---')
result_delete = model.delete_atencion_medica(1 if node == 'quito' else 2, id_atencion, node=node)
print('Resultado eliminación:', result_delete)
