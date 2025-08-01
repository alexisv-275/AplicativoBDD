/**
 * Pacientes.js - Manejo del frontend para el módulo de pacientes
 * Funciones para cargar, mostrar y manipular datos de Vista_Paciente
 */

class PacientesManager {
    constructor() {
        this.currentNode = null;
        this.pacientes = [];
        this.filteredPacientes = [];
        this.searchTimeout = null;
        this.init();
    }

    init() {
        // Cargar datos iniciales
        this.loadPacientes();
        
        // Configurar event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón actualizar
        const btnActualizar = document.querySelector('[onclick="loadPacientes()"]');
        if (btnActualizar) {
            btnActualizar.removeAttribute('onclick');
            btnActualizar.addEventListener('click', () => this.loadPacientes());
        }

        // Buscador
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Filtro de sexo
        const sexoFilter = document.getElementById('filterSexo');
        if (sexoFilter) {
            sexoFilter.addEventListener('change', () => this.applyFilters());
        }
    }

    async loadPacientes() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/pacientes');
            const data = await response.json();
            
            if (data.success) {
                // Asegurar que tenemos un array válido
                this.pacientes = Array.isArray(data.pacientes) ? data.pacientes : [];
                this.filteredPacientes = [...this.pacientes];
                this.currentNode = data.node;
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
                this.showSuccess(`Cargados ${data.total || 0} pacientes desde Vista_Paciente (${data.node})`);
            } else {
                this.pacientes = [];
                this.filteredPacientes = [];
                this.showError('Error al cargar pacientes: ' + data.error);
            }
        } catch (error) {
            this.pacientes = [];
            this.filteredPacientes = [];
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async searchPacientes(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredPacientes = [...this.pacientes];
            this.updateTable();
            return;
        }

        try {
            const response = await fetch(`/api/pacientes/search?q=${encodeURIComponent(searchTerm)}`);
            const data = await response.json();
            
            if (data.success) {
                // Asegurar que tenemos un array válido
                this.filteredPacientes = Array.isArray(data.pacientes) ? data.pacientes : [];
                this.updateTable();
                this.updateStats(data.total || 0, data.node);
            } else {
                this.filteredPacientes = [];
                this.showError('Error en la búsqueda: ' + data.error);
            }
        } catch (error) {
            this.filteredPacientes = [];
            this.showError('Error de búsqueda: ' + error.message);
        }
    }

    handleSearch(searchTerm) {
        // Debounce para evitar muchas peticiones
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.searchPacientes(searchTerm);
        }, 500);
    }

    applyFilters() {
        const sexoFilter = document.getElementById('filterSexo');
        
        // Asegurar que pacientes es un array válido
        let filtered = Array.isArray(this.pacientes) ? [...this.pacientes] : [];
        
        // Filtro por sexo
        if (sexoFilter && sexoFilter.value && sexoFilter.value !== '') {
            const sexo = sexoFilter.value === 'Masculino' ? 'M' : 'F';
            filtered = filtered.filter(p => p.Sexo === sexo);
        }
        
        this.filteredPacientes = filtered;
        this.updateTable();
        this.updateStats(filtered.length, this.currentNode);
    }

    updateTable() {
        const tbody = document.getElementById('tbody-pacientes') || 
                     document.querySelector('tbody');
        
        if (!tbody) {
            console.error('No se encontró el tbody de la tabla');
            return;
        }

        // Asegurar que filteredPacientes es un array válido
        const pacientes = Array.isArray(this.filteredPacientes) ? this.filteredPacientes : [];

        if (pacientes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center text-muted py-4">
                        <i class="bi bi-database-x"></i> 
                        No hay pacientes disponibles en Vista_Paciente
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        pacientes.forEach(paciente => {
            const nodeColor = paciente.ID_Hospital === 1 ? 'success' : 'info';
            const nodeName = paciente.ID_Hospital === 1 ? 'Quito' : 'Guayaquil';
            
            html += `
                <tr data-id-hospital="${paciente.ID_Hospital}" data-id-paciente="${paciente.ID_Paciente}">
                    <td class="text-center"><strong>${paciente.ID_Hospital}</strong></td>
                    <td class="text-center"><strong>${paciente.ID_Paciente}</strong></td>
                    <td>${this.escapeHtml(paciente.Nombre || 'N/A')}</td>
                    <td>${this.escapeHtml(paciente.Apellido || 'N/A')}</td>
                    <td>${this.escapeHtml(paciente.Direccion || 'Sin dirección')}</td>
                    <td class="text-center">${paciente.FechaNacimiento || 'N/A'}</td>
                    <td class="text-center">${paciente.Sexo || 'N/A'}</td>
                    <td>${this.escapeHtml(paciente.Telefono || 'Sin teléfono')}</td>
                    <td class="text-center">
                        <span class="badge bg-${nodeColor}">${nodeName}</span>
                    </td>
                    <td class="text-center">
                        <button class="btn btn-sm btn-outline-warning me-1" 
                                onclick="pacientesManager.editPaciente(${paciente.ID_Hospital}, ${paciente.ID_Paciente})" 
                                title="Editar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" 
                                onclick="pacientesManager.deletePaciente(${paciente.ID_Hospital}, ${paciente.ID_Paciente})" 
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
            infoRegistros.textContent = `${total} pacientes`;
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
                    <td colspan="10" class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2 text-muted">Consultando Vista_Paciente...</p>
                    </td>
                </tr>
            `;
        }
    }

    showError(message) {
        // Solo mostrar toast/alert, NO modificar la tabla
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

    // Métodos para CRUD - Siguiendo el patrón de Personal Médico
    
    openAddModal() {
        // Limpiar formulario
        document.getElementById('paciente_form').reset();
        document.getElementById('paciente_id_hospital').value = '';
        document.getElementById('paciente_id_paciente').value = '';
        
        // Configurar modal para agregar
        document.getElementById('pacienteModalLabel').textContent = 'Agregar Nuevo Paciente';
        document.getElementById('btn_save_paciente').textContent = 'Guardar Paciente';
        document.getElementById('btn_save_paciente').setAttribute('onclick', 'pacientesManager.addPaciente()');
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('pacienteModal'));
        modal.show();
    }

    async addPaciente() {
        try {
            const formData = {
                'Nombre': document.getElementById('paciente_nombre').value.trim(),
                'Apellido': document.getElementById('paciente_apellido').value.trim(), 
                'Direccion': document.getElementById('paciente_direccion').value.trim(),
                'FechaNacimiento': document.getElementById('paciente_fecha_nacimiento').value,
                'Sexo': document.getElementById('paciente_sexo').value,
                'Telefono': document.getElementById('paciente_telefono').value.trim()
            };

            // Validaciones básicas
            if (!formData.Nombre || !formData.Apellido || !formData.FechaNacimiento || !formData.Sexo) {
                this.showError('Por favor complete todos los campos obligatorios');
                return;
            }

            console.log('🔍 DEBUG: Enviando datos para crear paciente:', formData);

            const response = await fetch('/api/pacientes/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            console.log('🔍 DEBUG: Respuesta del servidor:', data);

            if (data.success) {
                this.showSuccess(data.message || 'Paciente creado exitosamente');
                bootstrap.Modal.getInstance(document.getElementById('pacienteModal')).hide();
                this.loadPacientes(); // Recargar la tabla
            } else {
                this.showError('Error al crear paciente: ' + data.error);
            }

        } catch (error) {
            console.error('Error al agregar paciente:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async editPaciente(idHospital, idPaciente) {
        try {
            // Primero obtener los datos del paciente
            const response = await fetch(`/api/pacientes/${idHospital}/${idPaciente}`);
            const data = await response.json();

            if (data.success && data.paciente) {
                const paciente = data.paciente;
                
                // Llenar el formulario con los datos existentes
                document.getElementById('paciente_id_hospital').value = paciente.ID_Hospital;
                document.getElementById('paciente_id_paciente').value = paciente.ID_Paciente;
                document.getElementById('paciente_nombre').value = paciente.Nombre || '';
                document.getElementById('paciente_apellido').value = paciente.Apellido || '';
                document.getElementById('paciente_direccion').value = paciente.Direccion || '';
                document.getElementById('paciente_fecha_nacimiento').value = paciente.FechaNacimiento || '';
                document.getElementById('paciente_sexo').value = paciente.Sexo || '';
                document.getElementById('paciente_telefono').value = paciente.Telefono || '';

                // Configurar modal para editar
                document.getElementById('pacienteModalLabel').textContent = 'Editar Paciente';
                document.getElementById('btn_save_paciente').textContent = 'Actualizar Paciente';
                document.getElementById('btn_save_paciente').setAttribute('onclick', 'pacientesManager.updatePaciente()');

                // Mostrar modal
                const modal = new bootstrap.Modal(document.getElementById('pacienteModal'));
                modal.show();

            } else {
                this.showError('Error al cargar datos del paciente: ' + (data.error || 'Paciente no encontrado'));
            }

        } catch (error) {
            console.error('Error al editar paciente:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async updatePaciente() {
        try {
            const idHospital = document.getElementById('paciente_id_hospital').value;
            const idPaciente = document.getElementById('paciente_id_paciente').value;
            
            const formData = {
                'Nombre': document.getElementById('paciente_nombre').value.trim(),
                'Apellido': document.getElementById('paciente_apellido').value.trim(),
                'Direccion': document.getElementById('paciente_direccion').value.trim(),
                'FechaNacimiento': document.getElementById('paciente_fecha_nacimiento').value,
                'Sexo': document.getElementById('paciente_sexo').value,
                'Telefono': document.getElementById('paciente_telefono').value.trim()
            };

            // Validaciones básicas
            if (!formData.Nombre || !formData.Apellido || !formData.FechaNacimiento || !formData.Sexo) {
                this.showError('Por favor complete todos los campos obligatorios');
                return;
            }

            console.log('🔧 DEBUG: Actualizando paciente:', formData);

            const response = await fetch(`/api/pacientes/${idHospital}/${idPaciente}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            console.log('🔧 DEBUG: Respuesta actualización:', data);

            if (data.success) {
                this.showSuccess(data.message || 'Paciente actualizado exitosamente');
                bootstrap.Modal.getInstance(document.getElementById('pacienteModal')).hide();
                this.loadPacientes(); // Recargar la tabla
            } else {
                this.showError('Error al actualizar paciente: ' + data.error);
            }

        } catch (error) {
            console.error('Error al actualizar paciente:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }

    async deletePaciente(idHospital, idPaciente) {
        // Buscar el paciente en los datos para mostrar la información
        const paciente = this.filteredPacientes.find(p => 
            p.ID_Hospital === idHospital && p.ID_Paciente === idPaciente
        );
        
        if (!paciente) {
            this.showError('Paciente no encontrado');
            return;
        }
        
        console.log('🗑️ DEBUG DELETE - Iniciando eliminación:', { idHospital, idPaciente, paciente });
        
        // Crear modal de confirmación Bootstrap (siguiendo patrón de Personal Médico)
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
                            <p>¿Está seguro de eliminar al paciente?</p>
                            <div class="alert alert-light">
                                <strong>${this.escapeHtml(paciente.Nombre || 'N/A')} ${this.escapeHtml(paciente.Apellido || 'N/A')}</strong><br>
                                <small class="text-muted">
                                    Hospital: ${paciente.ID_Hospital} | ID Paciente: ${paciente.ID_Paciente}
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
                            <button type="button" class="btn btn-danger" onclick="pacientesManager.confirmDeletePaciente(${idHospital}, ${idPaciente})">
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

    async confirmDeletePaciente(idHospital, idPaciente) {
        console.log('🗑️ DEBUG DELETE - Confirmación recibida:', { idHospital, idPaciente });
        
        // Cerrar modal de confirmación
        const modalElement = document.getElementById('deleteConfirmModal');
        if (modalElement) {
            bootstrap.Modal.getInstance(modalElement).hide();
        }

        try {
            const response = await fetch(`/api/pacientes/${idHospital}/${idPaciente}`, {
                method: 'DELETE'
            });
            
            console.log('🗑️ DEBUG DELETE - Response status:', response.status);
            const data = await response.json();
            console.log('🗑️ DEBUG DELETE - Response data:', data);
            
            if (data.success) {
                this.showSuccess('Paciente eliminado exitosamente');
                this.loadPacientes(); // Recargar tabla
            } else {
                this.showError('Error al eliminar: ' + data.error);
            }
        } catch (error) {
            console.error('💥 Error en DELETE:', error);
            this.showError('Error de conexión: ' + error.message);
        }
    }
}

// Inicializar cuando el DOM esté listo
let pacientesManager;

document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar en la página de pacientes
    if (window.location.pathname.includes('pacientes') || document.querySelector('tbody')) {
        pacientesManager = new PacientesManager();
    }
});

// Funciones globales para compatibilidad (hasta migrar completamente)
function loadPacientes() {
    if (pacientesManager) {
        pacientesManager.loadPacientes();
    }
}

function updatePacientesTable(pacientes, node) {
    if (pacientesManager) {
        pacientesManager.pacientes = pacientes;
        pacientesManager.filteredPacientes = [...pacientes];
        pacientesManager.currentNode = node;
        pacientesManager.updateTable();
    }
}

function showError(message) {
    if (pacientesManager) {
        pacientesManager.showError(message);
    }
}
