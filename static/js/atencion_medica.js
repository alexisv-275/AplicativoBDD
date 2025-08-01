/**
 * AtencionMedica.js - Manejo del frontend para el módulo de atención médica
 * Funciones para cargar, mostrar y manipular datos de Vista_Atencion_Medica
 */

class AtencionMedicaManager {
    constructor() {
        this.currentNode = null;
        this.atenciones = [];
        this.filteredAtenciones = [];
        this.init();
    }

    init() {
        // Cargar datos iniciales
        this.loadAtenciones();
        
        // Configurar event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón actualizar
        const btnActualizar = document.querySelector('[onclick="loadAtenciones()"]');
        if (btnActualizar) {
            btnActualizar.removeAttribute('onclick');
            btnActualizar.addEventListener('click', () => this.loadAtenciones());
        }

        // Botón agregar atención médica
        const btnAdd = document.getElementById('btnAddAtencion');
        if (btnAdd) {
            btnAdd.addEventListener('click', () => this.showAddAtencionModal());
        }

        // Buscador
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filtro por tipo
        const tipoFilter = document.getElementById('filterTipo');
        if (tipoFilter) {
            tipoFilter.addEventListener('change', () => this.applyFilters());
        }
    }

    async loadAtenciones() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/atenciones');
            const data = await response.json();
            
            if (data.success) {
                // Asegurar que tenemos un array válido
                this.atenciones = Array.isArray(data.atenciones) ? data.atenciones : [];
                this.filteredAtenciones = [...this.atenciones];
                this.currentNode = data.node;
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
                this.showSuccess(`Cargadas ${data.total || 0} atenciones desde Vista_Atencion_Medica (${data.node})`);
            } else {
                this.atenciones = [];
                this.filteredAtenciones = [];
                this.showError('Error al cargar atenciones: ' + data.error);
            }
        } catch (error) {
            this.atenciones = [];
            this.filteredAtenciones = [];
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async searchAtenciones(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredAtenciones = [...this.atenciones];
            this.updateTable();
            return;
        }

        try {
            const response = await fetch(`/api/atenciones/search?q=${encodeURIComponent(searchTerm)}`);
            const data = await response.json();
            
            if (data.success) {
                // Asegurar que tenemos un array válido
                this.filteredAtenciones = Array.isArray(data.atenciones) ? data.atenciones : [];
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
            } else {
                this.filteredAtenciones = [];
                this.showError('Error en la búsqueda: ' + data.error);
            }
        } catch (error) {
            this.filteredAtenciones = [];
            this.showError('Error de búsqueda: ' + error.message);
        }
    }

    handleSearch(searchTerm) {
        // Debounce para evitar muchas peticiones
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.searchAtenciones(searchTerm);
        }, 500);
    }

    applyFilters() {
        const tipoFilter = document.getElementById('filterTipo');
        
        // Asegurar que tenemos un array válido
        let filtered = Array.isArray(this.atenciones) ? [...this.atenciones] : [];
        
        // Filtro por tipo de atención
        if (tipoFilter && tipoFilter.value && tipoFilter.value !== '') {
            const tipoId = parseInt(tipoFilter.value);
            filtered = filtered.filter(a => a.ID_Tipo === tipoId);
        }
        
        this.filteredAtenciones = filtered;
        this.updateTable();
        this.updateStats(filtered.length, this.currentNode);
    }

    updateTable() {
        const tbody = document.getElementById('tbody-atenciones') || 
                     document.querySelector('tbody');
        
        if (!tbody) {
            console.error('No se encontró el tbody de la tabla');
            return;
        }

        // Debug: Ver qué datos estamos recibiendo
        console.log('Datos de atenciones:', this.filteredAtenciones);

        // Asegurar que filteredAtenciones es un array válido
        const atenciones = Array.isArray(this.filteredAtenciones) ? this.filteredAtenciones : [];

        if (atenciones.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center text-muted py-4">
                        <i class="bi bi-database-x"></i> 
                        No hay atenciones médicas disponibles en Vista_Atencion_Medica
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        atenciones.forEach(atencion => {
            // Debug: Ver cada atención individualmente
            console.log('Atención individual:', atencion);
            
            const nodeColor = atencion.ID_Hospital === 1 ? 'success' : 'info';
            const nodeName = atencion.ID_Hospital === 1 ? 'Quito' : 'Guayaquil';
            
            html += `
                <tr data-id-hospital="${atencion.ID_Hospital}" data-id-atencion="${atencion['ID_Atención']}">
                    <td class="text-center"><strong>${atencion.ID_Hospital}</strong></td>
                    <td class="text-center"><strong>${atencion['ID_Atención']}</strong></td>
                    <td class="text-center">${atencion.ID_Paciente || 'N/A'}</td>
                    <td class="text-center">${atencion.ID_Personal || 'N/A'}</td>
                    <td class="text-center">${atencion.ID_Tipo || 'N/A'}</td>
                    <td class="text-center">${atencion.Fecha || 'N/A'}</td>
                    <td>${this.escapeHtml(atencion.Diagnostico || 'Sin diagnóstico')}</td>
                    <td>${this.escapeHtml(atencion['Descripción'] || 'Sin descripción')}</td>
                    <td>${this.escapeHtml(atencion.Tratamiento || 'Sin tratamiento')}</td>
                    <td class="text-center">
                        <span class="badge bg-${nodeColor}">${nodeName}</span>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-warning me-1" 
                                onclick="atencionMedicaManager.editAtencion(${atencion.ID_Hospital}, ${atencion['ID_Atención']})" 
                                title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="atencionMedicaManager.deleteAtencion(${atencion.ID_Hospital}, ${atencion['ID_Atención']})" 
                                title="Eliminar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });

        tbody.innerHTML = html;
    }

    updateStats(total, node) {
        // Actualizar contador en badge
        const badge = document.querySelector('.badge.bg-secondary');
        if (badge) {
            badge.textContent = `${total} registros`;
        }

        // Actualizar información en footer
        const infoRegistros = document.getElementById('info-registros');
        if (infoRegistros) {
            infoRegistros.textContent = `${total} atenciones médicas`;
        }

        // Actualizar información del nodo
        const nodeInfo = document.querySelector('.text-muted span.badge');
        if (nodeInfo && node) {
            const nodeName = node === 'quito' ? 'Quito (ASUSVIVOBOOK)' : 'Guayaquil (DESKTOP-5U7KKBV)';
            const nodeClass = node === 'quito' ? 'bg-success' : 'bg-info';
            nodeInfo.className = `badge ${nodeClass}`;
            nodeInfo.textContent = nodeName;
        }
    }

    showLoading() {
        const tbody = document.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2 text-muted">Consultando Vista_Atencion_Medica...</p>
                    </td>
                </tr>
            `;
        }
    }

    showError(message) {
        const tbody = document.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle"></i> ${this.escapeHtml(message)}
                    </td>
                </tr>
            `;
        }
        
        // También mostrar toast/alert si está disponible
        this.showToast(message, 'error');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showToast(message, type = 'info') {
        // Crear toast dinámico
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i>
                    ${this.escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Mostrar toast con Bootstrap
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remover después de ocultarse
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Modal de edición/creación (patrón Pacientes)
    showAtencionModal(editing = false, atencion = null) {
        // Remover modal anterior si existe
        const existingModal = document.getElementById('atencionEditModal');
        if (existingModal) existingModal.remove();

        // IDs únicos para campos
        const idPersonal = editing && atencion ? atencion.ID_Personal : '';
        const idPaciente = editing && atencion ? atencion.ID_Paciente : '';
        const idTipo = editing && atencion ? atencion.ID_Tipo : '';
        const fecha = editing && atencion ? (atencion.Fecha ? (atencion.Fecha.split('/').reverse().join('-')) : '') : '';
        const diagnostico = editing && atencion ? atencion.Diagnostico : '';
        const descripcion = editing && atencion ? atencion['Descripción'] : '';
        const tratamiento = editing && atencion ? atencion.Tratamiento : '';

        const modalHtml = `
            <div class="modal fade" id="atencionEditModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${editing ? 'Editar Atención Médica' : 'Nueva Atención Médica'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="atencionForm">
                                <div class="mb-2">
                                    <label for="edit_id_personal" class="form-label">ID Personal</label>
                                    <input type="number" class="form-control" id="edit_id_personal" value="${idPersonal}" ${editing ? 'readonly' : ''} required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_id_paciente" class="form-label">ID Paciente</label>
                                    <input type="number" class="form-control" id="edit_id_paciente" value="${idPaciente}" ${editing ? 'readonly' : ''} required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_id_tipo" class="form-label">ID Tipo</label>
                                    <input type="number" class="form-control" id="edit_id_tipo" value="${idTipo}" ${editing ? 'readonly' : ''} required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_fecha" class="form-label">Fecha</label>
                                    <input type="date" class="form-control" id="edit_fecha" value="${fecha}" required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_diagnostico" class="form-label">Diagnóstico</label>
                                    <input type="text" class="form-control" id="edit_diagnostico" value="${diagnostico || ''}" required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_descripcion" class="form-label">Descripción</label>
                                    <input type="text" class="form-control" id="edit_descripcion" value="${descripcion || ''}" required>
                                </div>
                                <div class="mb-2">
                                    <label for="edit_tratamiento" class="form-label">Tratamiento</label>
                                    <input type="text" class="form-control" id="edit_tratamiento" value="${tratamiento || ''}" required>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="bi bi-x-circle"></i> Cancelar
                            </button>
                            <button type="button" class="btn btn-primary" id="btnSaveAtencion">
                                <i class="bi bi-save"></i> Guardar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('atencionEditModal'));
        modal.show();
        document.getElementById('btnSaveAtencion').onclick = () => this.saveAtencion(editing, atencion);
    }

    editAtencion(idHospital, idAtencion) {
        // Buscar la atención en la lista actual
        const atencion = this.atenciones.find(a => a.ID_Hospital === idHospital && a['ID_Atención'] === idAtencion);
        if (!atencion) {
            this.showError('No se encontró la atención médica');
            return;
        }
        this.showAtencionModal(true, atencion);
    }

    showAddAtencionModal() {
        this.showAtencionModal(false, null);
    }

    saveAtencion(editing, atencion) {
        // Obtener valores del formulario
        const idPersonal = document.getElementById('edit_id_personal').value;
        const idPaciente = document.getElementById('edit_id_paciente').value;
        const idTipo = document.getElementById('edit_id_tipo').value;
        const fecha = document.getElementById('edit_fecha').value;
        const diagnostico = document.getElementById('edit_diagnostico').value;
        const descripcion = document.getElementById('edit_descripcion').value;
        const tratamiento = document.getElementById('edit_tratamiento').value;
        if (!idPersonal || !idPaciente || !idTipo || !fecha || !diagnostico || !descripcion || !tratamiento) {
            this.showError('Por favor complete todos los campos obligatorios');
            return;
        }
        const atencionData = {
            ID_Personal: parseInt(idPersonal),
            ID_Paciente: parseInt(idPaciente),
            ID_Tipo: parseInt(idTipo),
            Fecha: fecha,
            Diagnostico: diagnostico,
            'Descripción': descripcion,
            Tratamiento: tratamiento
        };
        let url, method;
        if (editing && atencion) {
            url = `/api/atenciones/${atencion.ID_Hospital}/${atencion['ID_Atención']}`;
            method = 'PUT';
        } else {
            url = '/api/atenciones/add';
            method = 'POST';
        }
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(atencionData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showSuccess(data.message || 'Atención médica guardada exitosamente');
                this.loadAtenciones();
                const modal = bootstrap.Modal.getInstance(document.getElementById('atencionEditModal'));
                modal.hide();
            } else {
                this.showError('Error: ' + data.error);
            }
        })
        .catch(error => {
            this.showError('Error de conexión al guardar atención: ' + error);
        });
    }

    // Modal de eliminación estandarizado
    async deleteAtencion(idHospital, idAtencion) {
        // Modal de confirmación siguiendo el patrón Pacientes/Contratos
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
                            <p>¿Está seguro de eliminar esta atención médica?</p>
                            <div class="alert alert-light">
                                <strong>Hospital ID: ${idHospital} | Atención ID: ${idAtencion}</strong><br>
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
                            <button type="button" class="btn btn-danger" id="btnConfirmDeleteAtencion">
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
        const modal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        modal.show();
        document.getElementById('btnConfirmDeleteAtencion').onclick = () => this.confirmDeleteAtencion(idHospital, idAtencion);
    }

    confirmDeleteAtencion(idHospital, idAtencion) {
        // Cerrar modal de confirmación
        const modalElement = document.getElementById('deleteConfirmModal');
        if (modalElement) {
            bootstrap.Modal.getInstance(modalElement).hide();
        }
        fetch(`/api/atenciones/${idHospital}/${idAtencion}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showSuccess(data.message || 'Atención médica eliminada exitosamente');
                this.loadAtenciones();
            } else {
                this.showError('Error al eliminar atención médica: ' + (data.error || 'Error desconocido'));
            }
        })
        .catch(error => {
            this.showError('Error de conexión al eliminar atención médica: ' + error);
        });
    }
}

// Inicializar cuando el DOM esté listo
let atencionMedicaManager;

document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar en la página de atención médica/citas
    if (window.location.pathname.includes('citas') || window.location.pathname.includes('atencion') || document.querySelector('tbody')) {
        atencionMedicaManager = new AtencionMedicaManager();
    }
});

// Funciones globales para compatibilidad (hasta migrar completamente)
function loadAtenciones() {
    if (atencionMedicaManager) {
        atencionMedicaManager.loadAtenciones();
    }
}

function updateAtencionesTable(atenciones, node) {
    if (atencionMedicaManager) {
        atencionMedicaManager.atenciones = atenciones;
        atencionMedicaManager.filteredAtenciones = [...atenciones];
        atencionMedicaManager.currentNode = node;
        atencionMedicaManager.updateTable();
    }
}

function showError(message) {
    if (atencionMedicaManager) {
        atencionMedicaManager.showError(message);
    }
}
