// Variables globales
let tiposAtencionData = [];
let currentNode = 'quito';

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadTiposAtencion();
    initializeEventListeners();
});

function initializeEventListeners() {
    // Botón actualizar
    const btnActualizar = document.querySelector('[onclick="loadTiposAtencion()"]');
    if (btnActualizar) {
        btnActualizar.removeAttribute('onclick');
        btnActualizar.addEventListener('click', () => loadTiposAtencion());
    }

    // Buscar tipos de atención
    const searchInput = document.querySelector('input[placeholder*="Buscar"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim();
            if (searchTerm.length >= 3 || searchTerm.length === 0) {
                searchTiposAtencion(searchTerm);
            }
        });
    }

    // Botón nuevo tipo de atención
    const btnNuevo = document.querySelector('.btn-success');
    if (btnNuevo) {
        btnNuevo.addEventListener('click', showAddModal);
    }
}

function loadTiposAtencion() {
    showLoading(true);
    
    fetch('/api/tipos-atencion')
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                tiposAtencionData = data.tipos_atencion;
                currentNode = data.node;
                updateTable(tiposAtencionData);
                updateNodeIndicator(data.node);
                updateTipoAtencionStats(data.total);
                showSuccess(`Cargados ${data.total || 0} tipos de atención desde tabla Tipo_Atención (${data.node})`);
            } else {
                showError('Error al cargar tipos de atención: ' + data.error);
                updateTable([]);
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showError('Error de conexión al cargar tipos de atención');
            updateTable([]);
        });
}

function updateTable(tiposAtencion) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (tiposAtencion.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center py-4">
                    <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2">No se encontraron tipos de atención</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tiposAtencion.forEach(tipoAtencion => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="text-center"><strong>${tipoAtencion.ID_Tipo}</strong></td>
            <td>${tipoAtencion.Tipo}</td>
            <td class="text-center">
                <button class="btn btn-sm btn-outline-warning me-1" 
                        onclick="editTipoAtencion(${tipoAtencion.ID_Tipo})" 
                        title="Editar">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" 
                        onclick="deleteTipoAtencion(${tipoAtencion.ID_Tipo})" 
                        title="Eliminar">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function searchTiposAtencion(searchTerm) {
    if (!searchTerm) {
        updateTable(tiposAtencionData);
        return;
    }
    
    showLoading(true);
    
    fetch(`/api/tipos-atencion/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.success) {
                updateTable(data.tipos_atencion);
                updateTipoAtencionStats(data.total);
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
        <div class="modal fade" id="tipoAtencionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-plus-circle"></i> Nuevo Tipo de Atención
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="tipoAtencionForm">
                            <div class="mb-3">
                                <label for="tipo" class="form-label">Tipo de Atención *</label>
                                <input type="text" class="form-control" id="tipo" required>
                                <div class="form-text">Ingrese el nombre del tipo de atención médica</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" onclick="saveTipoAtencion()">
                            <i class="bi bi-check-circle"></i> Guardar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.getElementById('tipoAtencionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('tipoAtencionModal'));
    modal.show();
}

function editTipoAtencion(id) {
    const tipoAtencion = tiposAtencionData.find(t => t.ID_Tipo === id);
    if (!tipoAtencion) return;
    
    const modalHtml = `
        <div class="modal fade" id="tipoAtencionModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-pencil"></i> Editar Tipo de Atención
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="tipoAtencionForm">
                            <input type="hidden" id="tipoAtencionId" value="${tipoAtencion.ID_Tipo}">
                            <div class="mb-3">
                                <label for="tipo" class="form-label">Tipo de Atención *</label>
                                <input type="text" class="form-control" id="tipo" value="${tipoAtencion.Tipo}" required>
                                <div class="form-text">Modifique el nombre del tipo de atención médica</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-warning" onclick="updateTipoAtencion()">
                            <i class="bi bi-check-circle"></i> Actualizar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.getElementById('tipoAtencionModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Mostrar modal
    const modal = new bootstrap.Modal(document.getElementById('tipoAtencionModal'));
    modal.show();
}

function saveTipoAtencion() {
    const tipo = document.getElementById('tipo').value.trim();
    
    if (!tipo) {
        showError('El tipo de atención es obligatorio');
        return;
    }
    
    const data = {
        Tipo: tipo
    };
    
    fetch('/api/tipos-atencion/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Tipo de atención agregado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('tipoAtencionModal')).hide();
            loadTiposAtencion(); // Recargar datos
        } else {
            showError('Error al agregar tipo de atención: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al agregar tipo de atención');
    });
}

function updateTipoAtencion() {
    const id = document.getElementById('tipoAtencionId').value;
    const tipo = document.getElementById('tipo').value.trim();
    
    if (!tipo) {
        showError('El tipo de atención es obligatorio');
        return;
    }
    
    const data = {
        Tipo: tipo
    };
    
    fetch(`/api/tipos-atencion/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Tipo de atención actualizado exitosamente');
            bootstrap.Modal.getInstance(document.getElementById('tipoAtencionModal')).hide();
            loadTiposAtencion(); // Recargar datos
        } else {
            showError('Error al actualizar tipo de atención: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al actualizar tipo de atención');
    });
}

function deleteTipoAtencion(id) {
    const tipoAtencion = tiposAtencionData.find(t => t.ID_Tipo === id);
    if (!tipoAtencion) return;

    // Rellenar el contenido del modal
    const modalBody = document.getElementById('deleteTipoAtencionModalBody');
    if (modalBody) {
        modalBody.innerHTML = `
            <p>¿Está seguro de eliminar el tipo de atención?</p>
            <div class="alert alert-light">
                <strong>${tipoAtencion.Tipo || 'N/A'}</strong><br>
                <small class="text-muted">ID Tipo: ${tipoAtencion.ID_Tipo}</small>
            </div>
            <p class="text-danger">
                <i class="bi bi-exclamation-circle"></i>
                <strong>Esta acción no se puede deshacer.</strong>
            </p>
        `;
    }

    // Configurar el botón de confirmación
    const confirmBtn = document.getElementById('confirmDeleteTipoAtencionBtn');
    if (confirmBtn) {
        confirmBtn.onclick = function() {
            confirmDeleteTipoAtencion(id);
        };
    }

    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('deleteTipoAtencionModal'));
    modal.show();
}

function confirmDeleteTipoAtencion(id) {
    // Cerrar modal
    const modalElement = document.getElementById('deleteTipoAtencionModal');
    if (modalElement) {
        bootstrap.Modal.getInstance(modalElement).hide();
    }

    fetch(`/api/tipos-atencion/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccess('Tipo de atención eliminado exitosamente');
            loadTiposAtencion(); // Recargar datos
        } else {
            showError('Error al eliminar tipo de atención: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('Error de conexión al eliminar tipo de atención');
    });
}

function updateNodeIndicator(node) {
    // Actualizar indicador de nodo si existe
    const nodeIndicator = document.querySelector('.node-indicator');
    if (nodeIndicator) {
        nodeIndicator.textContent = `Nodo: ${node}`;
    }
}

function updateTipoAtencionStats(total) {
    // Actualizar contador de tipos de atención
    const badge = document.querySelector('.badge.bg-secondary');
    if (badge) {
        badge.textContent = `${total} tipos de atención`;
    }
    
    // Actualizar footer
    const footer = document.querySelector('.card-footer small');
    if (footer) {
        footer.innerHTML = `
            <i class="bi bi-mouse"></i> Desplázate para ver más tipos de atención • 
            <strong>${total}</strong> tipos de atención médica mostrados
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
                    <p class="text-muted mt-2 mb-0">Cargando tipos de atención...</p>
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
