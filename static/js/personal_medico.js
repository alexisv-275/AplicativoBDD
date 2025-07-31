// Variables globales
let personalMedicoData = [];
let currentNode = 'quito';

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadPersonalMedico();
    initializeEventListeners();
});

function initializeEventListeners() {
    // Botón actualizar
    const btnActualizar = document.querySelector('[onclick="loadPersonalMedico()"]');
    if (btnActualizar) {
        btnActualizar.removeAttribute('onclick');
        btnActualizar.addEventListener('click', () => loadPersonalMedico());
    }

    // Buscar personal médico
    const searchInput = document.querySelector('input[placeholder*="Buscar"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            if (searchTerm.length >= 3 || searchTerm.length === 0) {
                searchPersonalMedico(searchTerm);
            }
        });
    }

    // Botón nuevo personal médico - usar el botón del modal
    const btnNuevo = document.querySelector('button[data-bs-target="#modalNuevoPersonal"]');
    if (btnNuevo) {
        btnNuevo.addEventListener('click', showAddModal);
    }
    
    // Configurar el formulario del modal
    const form = document.getElementById('formNuevoPersonal');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            savePersonalMedicoWithContrato();
        });
    }
}

function loadPersonalMedico() {
    showLoading(true);
    
    fetch('/api/personal-medico')
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                personalMedicoData = data.personal_medico;
                currentNode = data.node;
                updateTable(personalMedicoData);
                updateNodeIndicator(data.node);
                updatePersonalMedicoStats(data.total);
                showSuccess(`Cargados ${data.total || 0} registros de personal médico desde Vista_INF_Personal (${data.node})`);
            } else {
                showError('Error al cargar personal médico: ' + data.error);
                updateTable([]);
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showError('Error de conexión al cargar personal médico');
            updateTable([]);
        });
}

function updateTable(personalMedico) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (personalMedico.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2">No se encontró personal médico</p>
                </td>
            </tr>
        `;
        return;
    }
    
    personalMedico.forEach(personal => {
        const nodeColor = personal.ID_Hospital === 1 ? 'success' : 'info';
        const nodeName = personal.ID_Hospital === 1 ? 'Quito' : 'Guayaquil';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center"><strong>${personal.ID_Hospital}</strong></td>
            <td class="text-center"><strong>${personal.ID_Personal}</strong></td>
            <td class="text-center">${personal.ID_Especialidad || 'N/A'}</td>
            <td>${personal.Nombre || 'N/A'}</td>
            <td>${personal.Apellido || 'N/A'}</td>
            <td>${personal.Teléfono || 'N/A'}</td>
            <td class="text-center">
                <span class="badge bg-${nodeColor}">${nodeName}</span>
            </td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-warning me-1" 
                        onclick="editPersonalMedico(${personal.ID_Hospital}, ${personal.ID_Personal})" 
                        title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="deletePersonalMedico(${personal.ID_Hospital}, ${personal.ID_Personal})" 
                        title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function searchPersonalMedico(searchTerm) {
    if (!searchTerm) {
        updateTable(personalMedicoData);
        return;
    }
    
    showLoading(true);
    
    fetch(`/api/personal-medico/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                updateTable(data.personal_medico);
                updatePersonalMedicoStats(data.total);
            } else {
                showError('Error en la búsqueda: ' + data.error);
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showError('Error de conexión en la búsqueda');
        });
}

function showAddModal() {
    // Limpiar formulario
    const form = document.getElementById('formNuevoPersonal');
    if (form) {
        form.reset();
    }
    
    // Establecer fecha actual como default
    const fechaInput = document.getElementById('fechaContrato');
    if (fechaInput) {
        const today = new Date().toISOString().split('T')[0];
        fechaInput.value = today;
    }
}

function savePersonalMedicoWithContrato() {
    console.log('📝 Iniciando savePersonalMedicoWithContrato...');
    
    const form = document.getElementById('formNuevoPersonal');
    if (!form) {
        console.error('❌ No se encontró el formulario');
        return;
    }
    
    const formData = new FormData(form);
    
    // Preparar datos del personal médico
    const personalData = {
        ID_Especialidad: parseInt(formData.get('especialidad')),
        Nombre: formData.get('nombre'),
        Apellido: formData.get('apellido'),
        Teléfono: formData.get('telefono')
    };
    
    // Preparar datos del contrato
    const salario = parseFloat(formData.get('salario'));
    const fechaContrato = formData.get('fechaContrato') || null;
    
    console.log('📋 Datos a enviar:', {
        personal_data: personalData,
        salario: salario,
        fecha_contrato: fechaContrato
    });
    
    // Enviar datos al servidor
    fetch('/api/personal-medico-with-contrato', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            personal_data: personalData,
            salario: salario,
            fecha_contrato: fechaContrato
        })
    })
    .then(response => {
        console.log('📡 Respuesta del servidor:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Datos recibidos:', data);
        
        if (data.success) {
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('modalNuevoPersonal'));
            if (modal) {
                modal.hide();
            }
            
            // Recargar datos
            loadPersonalMedico();
            
            // Mostrar mensaje de éxito
            showToast('Personal médico y contrato creados exitosamente', 'success');
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('💥 Error en fetch:', error);
        showToast('Error al crear personal médico y contrato', 'error');
    });
}

function editPersonalMedico(idHospital, idPersonal) {
    const personal = personalMedicoData.find(p => p.ID_Hospital === idHospital && p.ID_Personal === idPersonal);
    if (!personal) return;
    
    const modalHtml = `
        <div class="modal fade" id="personalMedicoModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-pencil"></i> Editar Personal Médico
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="personalMedicoForm">
                            <input type="hidden" id="personalMedicoIdHospital" value="${personal.ID_Hospital}">
                            <input type="hidden" id="personalMedicoIdPersonal" value="${personal.ID_Personal}">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="id_hospital" class="form-label">ID Hospital *</label>
                                    <select class="form-control" id="id_hospital" required disabled>
                                        <option value="${personal.ID_Hospital}" selected>
                                            Hospital ${personal.ID_Hospital} - ${personal.ID_Hospital === 1 ? 'Quito' : 'Guayaquil'}
                                        </option>
                                    </select>
                                    <div class="form-text">El hospital no se puede modificar</div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="id_personal" class="form-label">ID Personal *</label>
                                    <input type="number" class="form-control" id="id_personal" value="${personal.ID_Personal}" required disabled>
                                    <div class="form-text">El ID personal no se puede modificar</div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="edit_id_especialidad" class="form-label">ID Especialidad *</label>
                                <input type="number" class="form-control" id="edit_id_especialidad" value="${personal.ID_Especialidad || ''}" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="edit_nombre" class="form-label">Nombre *</label>
                                    <input type="text" class="form-control" id="edit_nombre" value="${personal.Nombre || ''}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="edit_apellido" class="form-label">Apellido *</label>
                                    <input type="text" class="form-control" id="edit_apellido" value="${personal.Apellido || ''}" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="edit_telefono" class="form-label">Teléfono</label>
                                <input type="tel" class="form-control" id="edit_telefono" value="${personal.Teléfono || ''}">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-warning" onclick="updatePersonalMedico()">
                            <i class="bi bi-check-circle"></i> Actualizar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.getElementById('personalMedicoModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('personalMedicoModal'));
    modal.show();
}

function savePersonalMedico() {
    const idEspecialidad = document.getElementById('id_especialidad').value.trim();
    const nombre = document.getElementById('nombre').value.trim();
    const apellido = document.getElementById('apellido').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    
    if (!idEspecialidad || !nombre || !apellido) {
        showError('Todos los campos marcados con * son obligatorios');
        return;
    }
    
    const data = {
        ID_Especialidad: parseInt(idEspecialidad),
        Nombre: nombre,
        Apellido: apellido,
        Teléfono: telefono
    };
    
    fetch('/api/personal-medico/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess(`Personal médico agregado exitosamente con ID ${data.id_personal} en Hospital ${data.id_hospital}`);
            bootstrap.Modal.getInstance(document.getElementById('personalMedicoModal')).hide();
            loadPersonalMedico(); // Recargar datos
        } else {
            showError('Error al agregar personal médico: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al agregar personal médico');
    });
}

function updatePersonalMedico() {
    const idHospital = document.getElementById('personalMedicoIdHospital').value;
    const idPersonal = document.getElementById('personalMedicoIdPersonal').value;
    const idEspecialidad = document.getElementById('edit_id_especialidad').value.trim();
    const nombre = document.getElementById('edit_nombre').value.trim();
    const apellido = document.getElementById('edit_apellido').value.trim();
    const telefono = document.getElementById('edit_telefono').value.trim();
    
    console.log('🔧 DEBUG UPDATE - Valores del formulario:');
    console.log('  ID Hospital:', idHospital);
    console.log('  ID Personal:', idPersonal);
    console.log('  ID Especialidad:', idEspecialidad);
    console.log('  Nombre:', nombre);
    console.log('  Apellido:', apellido);
    console.log('  Teléfono:', telefono);
    
    if (!idEspecialidad || !nombre || !apellido) {
        console.log('❌ Validación fallida - campos vacíos');
        showError('Todos los campos marcados con * son obligatorios');
        return;
    }
    
    const data = {
        ID_Especialidad: parseInt(idEspecialidad),
        Nombre: nombre,
        Apellido: apellido,
        Teléfono: telefono
    };
    
    console.log('📤 Enviando datos:', data);
    console.log('📤 URL:', `/api/personal-medico/${idHospital}/${idPersonal}`);
    
    fetch(`/api/personal-medico/${idHospital}/${idPersonal}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('📡 Respuesta HTTP:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Respuesta del servidor:', data);
        
        if (data.success) {
            showSuccess('Personal médico actualizado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('personalMedicoModal')).hide();
            loadPersonalMedico(); // Recargar datos
        } else {
            showError('Error al actualizar personal médico: ' + data.error);
        }
    })
    .catch(error => {
        console.error('💥 Error en fetch:', error);
        showError('Error de conexión al actualizar personal médico');
    });
}

function deletePersonalMedico(idHospital, idPersonal) {
    const personal = personalMedicoData.find(p => p.ID_Hospital === idHospital && p.ID_Personal === idPersonal);
    if (!personal) return;
    
    console.log('🗑️ DEBUG DELETE - Iniciando eliminación:', { idHospital, idPersonal, personal });
    
    // Modal de confirmación siguiendo el patrón de Pacientes/Contratos
    const confirmModal = `
        <div class="modal fade" id="deleteConfirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle text-warning"></i>
                            Confirmar Eliminación
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>¿Está seguro de eliminar al personal médico?</p>
                        <div class="alert alert-light">
                            <strong>${personal.Nombre || 'N/A'} ${personal.Apellido || 'N/A'}</strong><br>
                            <small class="text-muted">
                                Hospital: ${personal.ID_Hospital} | ID Personal: ${personal.ID_Personal}
                            </small>
                        </div>
                        <p class="text-danger">
                            <i class="bi bi-exclamation-circle"></i>
                            <strong>Esta acción no se puede deshacer.</strong>
                        </p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" onclick="confirmDeletePersonalMedico(${idHospital}, ${idPersonal})">
                            <i class="bi bi-trash"></i> Eliminar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal anterior si existe y agregar nuevo
    const existingModal = document.getElementById('deleteConfirmModal');
    if (existingModal) existingModal.remove();
    
    document.body.insertAdjacentHTML('beforeend', confirmModal);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
    modal.show();
}

function confirmDeletePersonalMedico(idHospital, idPersonal) {
    console.log('🗑️ DEBUG DELETE - Confirmación recibida:', { idHospital, idPersonal });
    
    // Cerrar modal de confirmación
    bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal')).hide();
    
    fetch(`/api/personal-medico/${idHospital}/${idPersonal}`, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('🗑️ DEBUG DELETE - Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('🗑️ DEBUG DELETE - Response data:', data);
        if (data.success) {
            showSuccess('Personal médico eliminado exitosamente');
            loadPersonalMedico(); // Recargar datos
        } else {
            // Solo mostrar toast, NO modificar la tabla
            showError('Error al eliminar personal médico: ' + data.error);
        }
    })
    .catch(error => {
        console.error('💥 Error en DELETE:', error);
        showError('Error de conexión al eliminar personal médico');
    });
}

function updateNodeIndicator(node) {
    // Actualizar indicador de nodo si existe
    const nodeIndicator = document.querySelector('.node-indicator');
    if (nodeIndicator) {
        nodeIndicator.textContent = `Nodo: ${node}`;
    }
}

function updatePersonalMedicoStats(total) {
    // Actualizar contador de personal médico
    const badge = document.querySelector('.badge.bg-secondary');
    if (badge) {
        badge.textContent = `${total} registros`;
    }
    
    // Actualizar footer
    const footer = document.querySelector('.card-footer small');
    if (footer) {
        footer.innerHTML = `
            <i class="bi bi-mouse"></i> Desplázate para ver más personal médico • 
            <strong>${total}</strong> registros de personal médico mostrados
        `;
    }
}

function showLoading(show) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    if (show) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center py-4">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="text-muted mt-2 mb-0">Cargando personal médico...</p>
                </td>
            </tr>
        `;
    }
}

function showSuccess(message) {
    // Crear toast de éxito
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-check-circle"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover después de que se oculte
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function showError(message) {
    // Crear toast de error
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0 position-fixed top-0 end-0 m-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-exclamation-triangle"></i> ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remover después de que se oculte
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Función unificada para mostrar toasts
function showToast(message, type = 'success') {
    if (type === 'success') {
        showSuccess(message);
    } else if (type === 'error') {
        showError(message);
    }
}
