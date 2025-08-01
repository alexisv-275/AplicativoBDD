/**
 * Experiencia.js - Manejo del frontend para el módulo de experiencia médica
 * Funciones para cargar, mostrar y manipular datos de Vista_Experiencia
 */

class ExperienciaManager {
    constructor() {
        this.currentNode = null;
        this.experiencias = [];
        this.filteredExperiencias = [];
        this.searchTimeout = null;
        this.init();
    }

    init() {
        // Cargar datos iniciales
        this.loadExperiencias();
        
        // Configurar event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón actualizar
        const btnActualizar = document.querySelector('[onclick="loadExperiencias()"]');
        if (btnActualizar) {
            btnActualizar.removeAttribute('onclick');
            btnActualizar.addEventListener('click', () => this.loadExperiencias());
        }

        // Buscador
        const searchInput = document.querySelector('input[placeholder*="Buscar"]');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filtros
        const hospitalFilter = document.querySelectorAll('.form-select')[0];
        const cargoFilter = document.querySelectorAll('.form-select')[1];
        
        if (hospitalFilter) {
            hospitalFilter.addEventListener('change', () => this.applyFilters());
        }
        
        if (cargoFilter) {
            cargoFilter.addEventListener('change', () => this.applyFilters());
        }

        // Botón nueva experiencia
        const btnNueva = document.querySelector('.btn-success');
        if (btnNueva) {
            btnNueva.addEventListener('click', () => this.showAddModal());
        }

        // Botón guardar en modal
        const saveBtn = document.getElementById('saveExperienciaBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveExperiencia());
        }
    }

    async loadExperiencias() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/experiencias');
            const data = await response.json();
            
            if (data.success) {
                this.experiencias = Array.isArray(data.experiencias) ? data.experiencias : [];
                this.filteredExperiencias = [...this.experiencias];
                this.currentNode = data.node;
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
                this.showSuccess(`Cargadas ${data.total || 0} experiencias desde Vista_Experiencia (${data.node})`);
            } else {
                // Solo mostrar toast de error, NO vaciar las listas ni actualizar tabla
                this.showError('Error al cargar experiencias: ' + data.error);
            }
        } catch (error) {
            // Solo mostrar toast de error, NO vaciar las listas ni actualizar tabla  
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async searchExperiencias(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredExperiencias = [...this.experiencias];
            this.updateTable();
            return;
        }

        try {
            const response = await fetch(`/api/experiencias/search?q=${encodeURIComponent(searchTerm)}`);
            const data = await response.json();
            
            if (data.success) {
                this.filteredExperiencias = Array.isArray(data.experiencias) ? data.experiencias : [];
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
            } else {
                // Solo mostrar toast de error, NO vaciar la lista ni actualizar tabla
                this.showError('Error en la búsqueda: ' + data.error);
            }
        } catch (error) {
            // Solo mostrar toast de error, NO vaciar la lista ni actualizar tabla
            this.showError('Error de búsqueda: ' + error.message);
        }
    }

    handleSearch(searchTerm) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.searchExperiencias(searchTerm);
        }, 500);
    }

    applyFilters() {
        const hospitalFilter = document.querySelectorAll('.form-select')[0];
        const cargoFilter = document.querySelectorAll('.form-select')[1];
        
        let filtered = Array.isArray(this.experiencias) ? [...this.experiencias] : [];
        
        // Filtro por hospital
        if (hospitalFilter && hospitalFilter.value && hospitalFilter.value !== 'Todos los hospitales') {
            const hospitalId = hospitalFilter.value === 'Hospital 001' ? 1 : 2;
            filtered = filtered.filter(e => e.ID_Hospital === hospitalId);
        }
        
        // Filtro por cargo
        if (cargoFilter && cargoFilter.value && cargoFilter.value !== 'Todos los cargos') {
            filtered = filtered.filter(e => e.Cargo && e.Cargo.toLowerCase().includes(cargoFilter.value.toLowerCase()));
        }
        
        this.filteredExperiencias = filtered;
        this.updateTable();
        this.updateStats(filtered.length, this.currentNode);
    }

    updateTable() {
        const tbody = document.getElementById('tbody-experiencias') || document.querySelector('tbody');
        
        if (!tbody) {
            console.error('No se encontró el tbody de la tabla');
            return;
        }

        const experiencias = Array.isArray(this.filteredExperiencias) ? this.filteredExperiencias : [];

        if (experiencias.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="bi bi-database-x"></i> 
                        No hay experiencias disponibles en Vista_Experiencia
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        experiencias.forEach(experiencia => {
            const nodeColor = experiencia.ID_Hospital === 1 ? 'success' : 'info';
            const nodeName = experiencia.ID_Hospital === 1 ? 'Quito' : 'Guayaquil';
            
            html += `
                <tr data-id-hospital="${experiencia.ID_Hospital}" data-id-personal="${experiencia.ID_Personal}">
                    <td class="text-center"><strong>${experiencia.ID_Hospital}</strong></td>
                    <td class="text-center"><strong>${experiencia.ID_Personal}</strong></td>
                    <td>${this.escapeHtml(experiencia.Cargo || 'Sin cargo')}</td>
                    <td class="text-center">${experiencia.Años_exp !== null ? experiencia.Años_exp + ' años' : 'N/A'}</td>
                    <td class="text-center">
                        <span class="badge bg-${nodeColor}">${nodeName}</span>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-warning me-1" 
                                onclick="experienciaManager.editExperiencia(${experiencia.ID_Hospital}, ${experiencia.ID_Personal})" 
                                title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="experienciaManager.deleteExperiencia(${experiencia.ID_Hospital}, ${experiencia.ID_Personal}, '${this.escapeHtml(experiencia.Cargo)}')" 
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
            infoRegistros.textContent = `${total} experiencias`;
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
                    <td colspan="6" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2 text-muted">Consultando Vista_Experiencia...</p>
                    </td>
                </tr>
            `;
        }
    }

    showError(message) {
        // Solo mostrar toast, NO modificar la tabla (igual que en pacientes.js)
        this.showToast(message, 'error');
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showToast(message, type = 'info') {
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
        
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
            
            toast.addEventListener('hidden.bs.toast', () => {
                toast.remove();
            });
        }
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

    editExperiencia(idHospital, idPersonal) {
        // Buscar la experiencia en los datos
        const experiencia = this.filteredExperiencias.find(e => 
            e.ID_Hospital === idHospital && e.ID_Personal === idPersonal
        );
        
        if (!experiencia) {
            this.showError('Experiencia no encontrada');
            return;
        }
        
        this.showEditModal(experiencia);
    }

    showAddModal() {
        // Limpiar formulario
        document.getElementById('experienciaForm').reset();
        document.getElementById('edit_id_hospital').value = '';
        document.getElementById('edit_id_personal').value = '';
        document.getElementById('edit_cargo_original').value = '';
        
        // Configurar modal para agregar
        document.getElementById('experienciaModalTitle').innerHTML = 
            '<i class="bi bi-person-workspace"></i> Nueva Experiencia';
        document.getElementById('saveExperienciaBtn').innerHTML = 
            '<i class="bi bi-check-circle"></i> Guardar';
        
        // Habilitar campo ID_Personal para nueva experiencia (igual que Personal Médico)
        document.getElementById('id_personal').disabled = false;
        document.getElementById('id_personal').readOnly = false;
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('experienciaModal'));
        modal.show();
    }

    showEditModal(experiencia) {
        // Llenar formulario con datos existentes
        document.getElementById('edit_id_hospital').value = experiencia.ID_Hospital;
        document.getElementById('edit_id_personal').value = experiencia.ID_Personal;
        document.getElementById('edit_cargo_original').value = experiencia.Cargo;
        document.getElementById('id_personal').value = experiencia.ID_Personal;
        document.getElementById('cargo').value = experiencia.Cargo;
        document.getElementById('anios_exp').value = experiencia['Años_exp'] || 0;
        
        // Configurar modal para editar
        document.getElementById('experienciaModalTitle').innerHTML = 
            '<i class="bi bi-pencil"></i> Editar Experiencia';
        document.getElementById('saveExperienciaBtn').innerHTML = 
            '<i class="bi bi-check-circle"></i> Actualizar';
        
        // Deshabilitar campo ID_Personal para edición (igual que Personal Médico)
        document.getElementById('id_personal').disabled = true;
        document.getElementById('id_personal').readOnly = false;
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('experienciaModal'));
        modal.show();
    }

    async saveExperiencia() {
        const isEdit = document.getElementById('edit_id_hospital').value !== '';
        
        // Obtener valores directamente de los elementos (como en personal_medico.js)
        const idPersonal = document.getElementById('id_personal').value.trim();
        const cargo = document.getElementById('cargo').value.trim();
        const aniosExp = document.getElementById('anios_exp').value.trim();
        
        console.log('🔧 DEBUG: Valores del formulario:');
        console.log('  ID_Personal:', idPersonal);
        console.log('  Cargo:', cargo);
        console.log('  Anios_exp:', aniosExp);
        console.log('  Es edición:', isEdit);
        
        // Validaciones básicas
        if (!idPersonal || !cargo || !aniosExp) {
            console.log('❌ Validación fallida - campos vacíos');
            this.showError('Por favor complete todos los campos obligatorios');
            return;
        }

        // Validar rango de ID_Personal según nodo
        const idPersonalNum = parseInt(idPersonal);
        if (this.currentNode === 'quito' && (idPersonalNum < 1 || idPersonalNum > 10)) {
            this.showError('ID_Personal debe estar entre 1 y 10 para el nodo Quito');
            return;
        }
        if (this.currentNode === 'guayaquil' && (idPersonalNum < 11 || idPersonalNum > 20)) {
            this.showError('ID_Personal debe estar entre 11 y 20 para el nodo Guayaquil');
            return;
        }

        const data = {
            ID_Personal: idPersonal,
            Cargo: cargo,
            Anios_exp: aniosExp
        };
        
        try {
            let response;
            
            if (isEdit) {
                // Actualizar experiencia existente
                const idHospital = document.getElementById('edit_id_hospital').value;
                const idPersonalOriginal = document.getElementById('edit_id_personal').value;
                
                console.log('🔧 DEBUG: Actualizando experiencia:', { 
                    idHospital, 
                    idPersonalOriginal, 
                    data 
                });
                
                response = await fetch(`/api/experiencias/${idHospital}/${idPersonalOriginal}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
            } else {
                // Crear nueva experiencia
                console.log('🔧 DEBUG: Creando experiencia:', data);
                
                response = await fetch('/api/experiencias/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
            }

            const result = await response.json();
            console.log('🔧 DEBUG: Respuesta del servidor:', result);

            if (result.success) {
                this.showSuccess(result.message || (isEdit ? 'Experiencia actualizada exitosamente' : 'Experiencia creada exitosamente'));
                bootstrap.Modal.getInstance(document.getElementById('experienciaModal')).hide();
                this.loadExperiencias(); // Recargar la tabla
            } else {
                this.showError('Error al guardar experiencia: ' + result.error);
            }

        } catch (error) {
            console.error('Error al guardar experiencia:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async deleteExperiencia(idHospital, idPersonal, cargo) {
        // Buscar la experiencia en los datos para mostrar la información
        const experiencia = this.filteredExperiencias.find(e => 
            e.ID_Hospital === idHospital && e.ID_Personal === idPersonal && e.Cargo === cargo
        );
        
        if (!experiencia) {
            this.showError('Experiencia no encontrada');
            return;
        }
        
        console.log('🗑️ DEBUG DELETE - Iniciando eliminación:', { idHospital, idPersonal, cargo, experiencia });
        
        // Crear modal de confirmación Bootstrap (siguiendo patrón de Pacientes)
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
                            <p>¿Está seguro de eliminar la experiencia?</p>
                            <div class="alert alert-light">
                                <strong>${this.escapeHtml(experiencia.Cargo || 'N/A')}</strong><br>
                                <small class="text-muted">
                                    Hospital: ${experiencia.ID_Hospital} | ID Personal: ${experiencia.ID_Personal} | 
                                    Años: ${experiencia['Años_exp'] || 'N/A'}
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
                            <button type="button" class="btn btn-danger" onclick="experienciaManager.confirmDeleteExperiencia(${idHospital}, ${idPersonal}, '${this.escapeHtml(cargo)}')">
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

    async confirmDeleteExperiencia(idHospital, idPersonal, cargo) {
        console.log('🗑️ DEBUG DELETE - Confirmación recibida:', { idHospital, idPersonal, cargo });
        
        // Cerrar modal de confirmación
        const modalElement = document.getElementById('deleteConfirmModal');
        if (modalElement) {
            bootstrap.Modal.getInstance(modalElement).hide();
        }

        try {
            const response = await fetch(`/api/experiencias/${idHospital}/${idPersonal}/${encodeURIComponent(cargo)}`, {
                method: 'DELETE'
            });
            
            console.log('🗑️ DEBUG DELETE - Response status:', response.status);
            const data = await response.json();
            console.log('🗑️ DEBUG DELETE - Response data:', data);
            
            if (data.success) {
                this.showSuccess('Experiencia eliminada exitosamente');
                this.loadExperiencias(); // Recargar tabla
            } else {
                this.showError('Error al eliminar: ' + data.error);
            }
        } catch (error) {
            console.error('💥 Error en DELETE:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text ? text.replace(/[&<>"']/g, function(m) { return map[m]; }) : '';
    }
}

// Inicializar cuando el DOM esté listo
let experienciaManager;

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('experiencia') || document.querySelector('#tbody-experiencias')) {
        experienciaManager = new ExperienciaManager();
    }
});

// Funciones globales para compatibilidad
function loadExperiencias() {
    if (experienciaManager) {
        experienciaManager.loadExperiencias();
    }
}

function updateExperienciasTable(experiencias, node) {
    if (experienciaManager) {
        experienciaManager.experiencias = experiencias;
        experienciaManager.filteredExperiencias = [...experiencias];
        experienciaManager.currentNode = node;
        experienciaManager.updateTable();
    }
}

function showError(message) {
    if (experienciaManager) {
        experienciaManager.showError(message);
    }
}
