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

    // Botón nuevo personal médico
    const btnNuevo = document.querySelector('.btn-success');
    if (btnNuevo) {
        btnNuevo.addEventListener('click', showAddModal);
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
    const modalHtml = `
        <div class="modal fade" id="personalMedicoModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-plus-circle"></i> Nuevo Personal Médico
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info mb-3">
                            <i class="bi bi-info-circle"></i> 
                            Los IDs se asignan automáticamente según el nodo actual
                        </div>
                        <form id="personalMedicoForm">
                            <div class="mb-3">
                                <label for="id_especialidad" class="form-label">ID Especialidad *</label>
                                <input type="number" class="form-control" id="id_especialidad" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="nombre" class="form-label">Nombre *</label>
                                    <input type="text" class="form-control" id="nombre" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="apellido" class="form-label">Apellido *</label>
                                    <input type="text" class="form-control" id="apellido" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="telefono" class="form-label">Teléfono</label>
                                <input type="tel" class="form-control" id="telefono">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="savePersonalMedico()">
                            <i class="bi bi-check-circle"></i> Guardar
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
                                <label for="id_especialidad" class="form-label">ID Especialidad *</label>
                                <input type="number" class="form-control" id="id_especialidad" value="${personal.ID_Especialidad || ''}" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="nombre" class="form-label">Nombre *</label>
                                    <input type="text" class="form-control" id="nombre" value="${personal.Nombre || ''}" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="apellido" class="form-label">Apellido *</label>
                                    <input type="text" class="form-control" id="apellido" value="${personal.Apellido || ''}" required>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="telefono" class="form-label">Teléfono</label>
                                <input type="tel" class="form-control" id="telefono" value="${personal.Teléfono || ''}">
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
    
    fetch(`/api/personal-medico/${idHospital}/${idPersonal}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Personal médico actualizado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('personalMedicoModal')).hide();
            loadPersonalMedico(); // Recargar datos
        } else {
            showError('Error al actualizar personal médico: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al actualizar personal médico');
    });
}

function deletePersonalMedico(idHospital, idPersonal) {
    const personal = personalMedicoData.find(p => p.ID_Hospital === idHospital && p.ID_Personal === idPersonal);
    if (!personal) return;
    
    if (confirm(`¿Está seguro de eliminar al personal médico "${personal.Nombre} ${personal.Apellido}"?`)) {
        fetch(`/api/personal-medico/${idHospital}/${idPersonal}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess('Personal médico eliminado exitosamente');
                loadPersonalMedico(); // Recargar datos
            } else {
                showError('Error al eliminar personal médico: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Error de conexión al eliminar personal médico');
        });
    }
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
