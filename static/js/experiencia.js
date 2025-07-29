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
                this.experiencias = [];
                this.filteredExperiencias = [];
                this.showError('Error al cargar experiencias: ' + data.error);
            }
        } catch (error) {
            this.experiencias = [];
            this.filteredExperiencias = [];
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
                this.filteredExperiencias = [];
                this.showError('Error en la búsqueda: ' + data.error);
            }
        } catch (error) {
            this.filteredExperiencias = [];
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
                                onclick="experienciaManager.deleteExperiencia(${experiencia.ID_Hospital}, ${experiencia.ID_Personal})" 
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
        const tbody = document.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger py-4">
                        <i class="bi bi-exclamation-triangle"></i> ${this.escapeHtml(message)}
                    </td>
                </tr>
            `;
        }
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
        alert(`Editar experiencia ${idHospital}-${idPersonal}`);
    }

    async deleteExperiencia(idHospital, idPersonal) {
        if (!confirm('¿Está seguro que desea eliminar esta experiencia?')) {
            return;
        }

        try {
            const response = await fetch(`/api/experiencias/${idHospital}/${idPersonal}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Experiencia eliminada exitosamente');
                this.loadExperiencias();
            } else {
                this.showError('Error al eliminar: ' + data.error);
            }
        } catch (error) {
            this.showError('Error de conexión: ' + error.message);
        }
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
