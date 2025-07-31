// ==================== GESTIÓN DE CONTRATOS ====================

let currentEditingContrato = null;

// Cargar todos los contratos desde la API
function loadContratos() {
    fetch('/api/contratos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateContratosTable(data.contratos);
                showToast('Contratos actualizados exitosamente', 'success');
                updateContratosCount(data.total);
            } else {
                showToast('Error al cargar contratos: ' + data.error, 'error');
                console.error('Error al cargar contratos:', data.error);
            }
        })
        .catch(error => {
            showToast('Error de conexión al cargar contratos', 'error');
            console.error('Error:', error);
        });
}

// Actualizar la tabla de contratos con nuevos datos
function updateContratosTable(contratos) {
    const tableBody = document.getElementById('contratosTableBody');
    
    if (!contratos || contratos.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="bi bi-inbox text-muted" style="font-size: 2rem;"></i>
                    <p class="text-muted mt-2">No hay contratos disponibles</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = contratos.map(contrato => {
        const nodoClass = contrato.ID_Hospital == 1 ? 'success' : 'info';
        const nodoText = contrato.ID_Hospital == 1 ? 'Quito' : 'Guayaquil';
        const salarioFormatted = contrato.Salario ? `$${parseFloat(contrato.Salario).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}` : 'N/A';
        const fechaFormatted = contrato.Fecha_Contrato ? new Date(contrato.Fecha_Contrato).toLocaleDateString('es-ES') : 'N/A';
        
        return `
            <tr>
                <td class="text-center"><strong>${contrato.ID_Hospital}</strong></td>
                <td class="text-center"><strong>${contrato.ID_Personal}</strong></td>
                <td class="text-center">${salarioFormatted}</td>
                <td class="text-center">${fechaFormatted}</td>
                <td class="text-center">
                    <span class="badge bg-${nodoClass}">${nodoText}</span>
                </td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-warning me-1" 
                            onclick="editContrato(${contrato.ID_Hospital}, ${contrato.ID_Personal})" 
                            title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" 
                            onclick="deleteContrato(${contrato.ID_Hospital}, ${contrato.ID_Personal})" 
                            title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Actualizar contador de contratos
function updateContratosCount(count) {
    const countElement = document.getElementById('contratosCount');
    const totalElement = document.getElementById('totalContratos');
    
    if (countElement) {
        countElement.textContent = `${count} registros`;
    }
    if (totalElement) {
        totalElement.textContent = count;
    }
}

// Buscar contratos
function searchContratos() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    
    if (searchTerm === '') {
        loadContratos();
        return;
    }
    
    fetch(`/api/contratos/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateContratosTable(data.contratos);
                updateContratosCount(data.total);
                
                if (data.contratos.length === 0) {
                    showToast('No se encontraron contratos con ese criterio', 'info');
                }
            } else {
                showToast('Error al buscar contratos: ' + data.error, 'error');
            }
        })
        .catch(error => {
            showToast('Error de conexión al buscar contratos', 'error');
            console.error('Error:', error);
        });
}

// Mostrar modal para agregar nuevo contrato
function showAddContratoModal() {
    currentEditingContrato = null;
    document.getElementById('contratoModalLabel').textContent = 'Nuevo Contrato';
    document.getElementById('contratoForm').reset();
    
    // Habilitar campos de ID
    document.getElementById('idHospital').disabled = false;
    document.getElementById('idPersonal').disabled = false;
    
    const modal = new bootstrap.Modal(document.getElementById('contratoModal'));
    modal.show();
}

// Editar contrato existente
function editContrato(idHospital, idPersonal) {
    currentEditingContrato = { id_hospital: idHospital, id_personal: idPersonal };
    document.getElementById('contratoModalLabel').textContent = 'Editar Contrato';
    
    // Deshabilitar campos de ID (no se pueden cambiar)
    document.getElementById('idHospital').disabled = true;
    document.getElementById('idPersonal').disabled = true;
    
    // Buscar el contrato en la tabla actual
    const rows = document.querySelectorAll('#contratosTableBody tr');
    for (let row of rows) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            const hospitalId = cells[0].textContent.trim();
            const personalId = cells[1].textContent.trim();
            
            if (hospitalId == idHospital && personalId == idPersonal) {
                // Llenar el formulario con los datos actuales
                document.getElementById('idHospital').value = idHospital;
                document.getElementById('idPersonal').value = idPersonal;
                
                // Extraer el salario (remover $ y comas)
                const salarioText = cells[2].textContent.trim();
                if (salarioText !== 'N/A') {
                    const salario = salarioText.replace(/[$,]/g, '');
                    document.getElementById('salario').value = salario;
                }
                
                // Fecha (convertir de formato español a formato input date)
                const fechaText = cells[3].textContent.trim();
                if (fechaText !== 'N/A') {
                    const fechaParts = fechaText.split('/');
                    if (fechaParts.length === 3) {
                        const fecha = `${fechaParts[2]}-${fechaParts[1].padStart(2, '0')}-${fechaParts[0].padStart(2, '0')}`;
                        document.getElementById('fechaContrato').value = fecha;
                    }
                }
                break;
            }
        }
    }
    
    const modal = new bootstrap.Modal(document.getElementById('contratoModal'));
    modal.show();
}

// Guardar contrato (crear o actualizar)
function saveContrato() {
    const idHospital = document.getElementById('idHospital').value;
    const idPersonal = document.getElementById('idPersonal').value;
    const salario = document.getElementById('salario').value;
    const fechaContrato = document.getElementById('fechaContrato').value;
    
    // Validaciones
    if (!idHospital || !idPersonal || !salario) {
        showToast('Por favor complete todos los campos obligatorios', 'error');
        return;
    }
    
    const contratoData = {
        id_hospital: parseInt(idHospital),
        id_personal: parseInt(idPersonal),
        salario: parseFloat(salario),
        fecha_contrato: fechaContrato || null
    };
    
    let url, method;
    if (currentEditingContrato) {
        // Actualizar contrato existente
        url = `/api/contratos/${currentEditingContrato.id_hospital}/${currentEditingContrato.id_personal}`;
        method = 'PUT';
    } else {
        // Crear nuevo contrato
        url = '/api/contratos/add';
        method = 'POST';
    }
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(contratoData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            loadContratos(); // Recargar la tabla
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('contratoModal'));
            modal.hide();
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showToast('Error de conexión al guardar contrato', 'error');
        console.error('Error:', error);
    });
}

// Eliminar contrato
function deleteContrato(idHospital, idPersonal) {
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
                        <p>¿Está seguro de eliminar este contrato?</p>
                        <div class="alert alert-light">
                            <strong>Hospital ID: ${idHospital} | Personal ID: ${idPersonal}</strong><br>
                            <small class="text-muted">
                                Contrato entre Hospital ${idHospital} y Personal ${idPersonal}
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
                        <button type="button" class="btn btn-danger" onclick="confirmDeleteContrato(${idHospital}, ${idPersonal})">
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

// Función para confirmar la eliminación
function confirmDeleteContrato(idHospital, idPersonal) {
    // Cerrar modal de confirmación
    const modalElement = document.getElementById('deleteConfirmModal');
    if (modalElement) {
        bootstrap.Modal.getInstance(modalElement).hide();
    }

    fetch(`/api/contratos/${idHospital}/${idPersonal}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message || 'Contrato eliminado exitosamente', 'success');
            loadContratos(); // Recargar la tabla
        } else {
            showToast('Error al eliminar contrato: ' + (data.error || 'Error desconocido'), 'error');
        }
    })
    .catch(error => {
        showToast('Error de conexión al eliminar contrato', 'error');
        console.error('Error:', error);
    });
}

// Función auxiliar para mostrar mensajes toast
function showToast(message, type = 'info') {
    // Crear toast si no existe el contenedor
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                <strong class="me-auto">Contratos</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Mostrar el toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 4000
    });
    toast.show();
    
    // Eliminar el toast del DOM después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Auto-cargar datos cuando estamos en la página de contratos
    if (window.location.pathname === '/contratos') {
        loadContratos();
    }
    
    // Configurar búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(searchContratos, 300);
        });
    }
});
