// Variables globales
let especialidadesData = [];
let currentNode = 'quito';

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadEspecialidades();
    initializeEventListeners();
});

function initializeEventListeners() {
    // Botón actualizar
    const btnActualizar = document.querySelector('[onclick="loadEspecialidades()"]');
    if (btnActualizar) {
        btnActualizar.removeAttribute('onclick');
        btnActualizar.addEventListener('click', () => loadEspecialidades());
    }

    // Buscar especialidades
    const searchInput = document.querySelector('input[placeholder*="Buscar"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            if (searchTerm.length >= 3 || searchTerm.length === 0) {
                searchEspecialidades(searchTerm);
            }
        });
    }

    // Botón nueva especialidad
    const btnNueva = document.querySelector('.btn-success');
    if (btnNueva) {
        btnNueva.addEventListener('click', showAddModal);
    }
}

function loadEspecialidades() {
    showLoading(true);
    
    fetch('/api/especialidades')
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                especialidadesData = data.especialidades;
                currentNode = data.node;
                updateTable(especialidadesData);
                updateNodeIndicator(data.node);
                updateEspecialidadStats(data.total);
                showSuccess(`Cargadas ${data.total || 0} especialidades desde tabla Especialidad (${data.node})`);
            } else {
                showError('Error al cargar especialidades: ' + data.error);
                updateTable([]);
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showError('Error de conexión al cargar especialidades');
            updateTable([]);
        });
}

function updateTable(especialidades) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (especialidades.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center py-4">
                    <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2">No se encontraron especialidades</p>
                </td>
            </tr>
        `;
        return;
    }
    
    especialidades.forEach(especialidad => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center"><strong>${especialidad.ID_Especialidad}</strong></td>
            <td>${especialidad.Área}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-warning me-1" 
                        onclick="editEspecialidad(${especialidad.ID_Especialidad})" 
                        title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="deleteEspecialidad(${especialidad.ID_Especialidad})" 
                        title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function searchEspecialidades(searchTerm) {
    if (!searchTerm) {
        updateTable(especialidadesData);
        return;
    }
    
    showLoading(true);
    
    fetch(`/api/especialidades/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                updateTable(data.especialidades);
                updateEspecialidadStats(data.total);
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
        <div class="modal fade" id="especialidadModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-plus-circle"></i> Nueva Especialidad
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="especialidadForm">
                            <div class="mb-3">
                                <label for="area" class="form-label">Área de Especialización *</label>
                                <input type="text" class="form-control" id="area" required>
                                <div class="form-text">Ingrese el nombre del área médica</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="saveEspecialidad()">
                            <i class="bi bi-check-circle"></i> Guardar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.getElementById('especialidadModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('especialidadModal'));
    modal.show();
}

function editEspecialidad(id) {
    const especialidad = especialidadesData.find(e => e.ID_Especialidad === id);
    if (!especialidad) return;
    
    const modalHtml = `
        <div class="modal fade" id="especialidadModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-pencil"></i> Editar Especialidad
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="especialidadForm">
                            <input type="hidden" id="especialidadId" value="${especialidad.ID_Especialidad}">
                            <div class="mb-3">
                                <label for="area" class="form-label">Área de Especialización *</label>
                                <input type="text" class="form-control" id="area" value="${especialidad.Área}" required>
                                <div class="form-text">Modifique el nombre del área médica</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-warning" onclick="updateEspecialidad()">
                            <i class="bi bi-check-circle"></i> Actualizar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.getElementById('especialidadModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('especialidadModal'));
    modal.show();
}

function saveEspecialidad() {
    const area = document.getElementById('area').value.trim();
    
    if (!area) {
        showError('El área es obligatoria');
        return;
    }
    
    const data = {
        Área: area
    };
    
    fetch('/api/especialidades/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Especialidad agregada exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('especialidadModal')).hide();
            loadEspecialidades(); // Recargar datos
        } else {
            showError('Error al agregar especialidad: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al agregar especialidad');
    });
}

function updateEspecialidad() {
    const id = document.getElementById('especialidadId').value;
    const area = document.getElementById('area').value.trim();
    
    if (!area) {
        showError('El área es obligatoria');
        return;
    }
    
    const data = {
        Área: area
    };
    
    fetch(`/api/especialidades/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Especialidad actualizada exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('especialidadModal')).hide();
            loadEspecialidades(); // Recargar datos
        } else {
            showError('Error al actualizar especialidad: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al actualizar especialidad');
    });
}

function deleteEspecialidad(id) {
    const especialidad = especialidadesData.find(e => e.ID_Especialidad === id);
    if (!especialidad) return;

    // Rellenar el contenido del modal
    const modalBody = document.getElementById('deleteEspecialidadModalBody');
    if (modalBody) {
        modalBody.innerHTML = `
            <p>¿Está seguro de eliminar la especialidad?</p>
            <div class="alert alert-light">
                <strong>${especialidad.Área || 'N/A'}</strong><br>
                <small class="text-muted">ID Especialidad: ${especialidad.ID_Especialidad}</small>
            </div>
            <p class="text-danger">
                <i class="bi bi-exclamation-circle"></i>
                <strong>Esta acción no se puede deshacer.</strong>
            </p>
        `;
    }

    // Configurar el botón de confirmación
    const confirmBtn = document.getElementById('confirmDeleteEspecialidadBtn');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            confirmDeleteEspecialidad(id);
        };
    }

    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('deleteEspecialidadModal'));
    modal.show();
}

function confirmDeleteEspecialidad(id) {
    // Cerrar modal
    const modalElement = document.getElementById('deleteEspecialidadModal');
    if (modalElement) {
        bootstrap.Modal.getInstance(modalElement).hide();
    }

    fetch(`/api/especialidades/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Especialidad eliminada exitosamente');
            loadEspecialidades(); // Recargar datos
        } else {
            showError('Error al eliminar especialidad: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al eliminar especialidad');
    });
}

function updateNodeIndicator(node) {
    // Actualizar indicador de nodo si existe
    const nodeIndicator = document.querySelector('.node-indicator');
    if (nodeIndicator) {
        nodeIndicator.textContent = `Nodo: ${node}`;
    }
}

function updateEspecialidadStats(total) {
    // Actualizar contador de especialidades
    const badge = document.querySelector('.badge.bg-secondary');
    if (badge) {
        badge.textContent = `${total} especialidades`;
    }
    
    // Actualizar footer
    const footer = document.querySelector('.card-footer small');
    if (footer) {
        footer.innerHTML = `
            <i class="bi bi-mouse"></i> Desplázate para ver más especialidades • 
            <strong>${total}</strong> especialidades médicas mostradas
        `;
    }
}

function showLoading(show) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    if (show) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center py-4">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="text-muted mt-2 mb-0">Cargando especialidades...</p>
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
