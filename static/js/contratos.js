// ==================== GESTIÓN DE CONTRATOS ====================

// Variables globales para manejo de datos
let contratosData = [];
let filteredContratos = [];
let currentEditingContrato = null;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Deshabilitar funcionalidades de creación y eliminación para mantener consistencia
    disableCreateDeleteFunctionality();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Cargar contratos al inicio
    loadContratos();
});

// Configurar event listeners
function setupEventListeners() {
    // Buscador
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', () => applyFilters());
    }
    
    // Filtro de hospital
    const hospitalFilter = document.getElementById('filterHospital');
    if (hospitalFilter) {
        hospitalFilter.addEventListener('change', () => applyFilters());
    }
}

// Deshabilitar creación y eliminación para mantener consistencia con Personal Médico
function disableCreateDeleteFunctionality() {
    // Ocultar botón "Nuevo Contrato"
    const btnNuevoContrato = document.querySelector('.btn-success');
    if (btnNuevoContrato) {
        btnNuevoContrato.style.display = 'none';
    }
    
    // Agregar mensaje informativo
    const headerDiv = document.querySelector('.col-md-8');
    if (headerDiv) {
        const infoMessage = document.createElement('div');
        infoMessage.className = 'alert alert-info mt-2';
        infoMessage.innerHTML = `
            <i class="bi bi-info-circle"></i>
            <strong>Modo Solo Lectura:</strong> Los contratos se crean y eliminan automáticamente desde el módulo 
            <strong>Personal Médico</strong> para mantener la consistencia de datos. Aquí solo puede ver y actualizar contratos existentes.
        `;
        headerDiv.appendChild(infoMessage);
    }
}

// Cargar todos los contratos desde la API
function loadContratos() {
    fetch('/api/contratos')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                contratosData = data.contratos || [];
                filteredContratos = [...contratosData];
                updateContratosTable(filteredContratos);
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
                    <!-- Botón eliminar deshabilitado para mantener consistencia -->
                    <button class="btn btn-sm btn-outline-secondary" 
                            disabled 
                            title="Eliminación deshabilitada - Use Personal Médico">
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

// Aplicar filtros de búsqueda y hospital
function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const hospitalFilter = document.getElementById('filterHospital');
    
    let filtered = [...contratosData];
    
    // Filtro por hospital
    if (hospitalFilter && hospitalFilter.value && hospitalFilter.value !== '') {
        const hospitalId = parseInt(hospitalFilter.value);
        filtered = filtered.filter(c => c.ID_Hospital === hospitalId);
    }
    
    // Filtro por búsqueda (ID personal o salario)
    if (searchTerm !== '') {
        filtered = filtered.filter(contrato => {
            const idPersonalMatch = contrato.ID_Personal && contrato.ID_Personal.toString().includes(searchTerm);
            const salarioMatch = contrato.Salario && contrato.Salario.toString().includes(searchTerm);
            
            return idPersonalMatch || salarioMatch;
        });
    }
    
    filteredContratos = filtered;
    updateContratosTable(filteredContratos);
    updateContratosCount(filteredContratos.length);
    
    if (searchTerm !== '' && filteredContratos.length === 0) {
        showToast('No se encontraron contratos con ese criterio', 'info');
    }
}

// Buscar contratos - FUNCIÓN MANTENIDA PARA COMPATIBILIDAD
function searchContratos() {
    applyFilters();
}

// Mostrar modal para agregar nuevo contrato - FUNCIÓN DESHABILITADA
function showAddContratoModal() {
    // Mostrar mensaje informativo en lugar de abrir modal
    showToast('La creación de contratos está deshabilitada. Use el módulo Personal Médico para crear contratos y mantener la consistencia de datos.', 'error');
    return;
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

// Eliminar contrato - FUNCIÓN DESHABILITADA
function deleteContrato(idHospital, idPersonal) {
    // Mostrar mensaje informativo en lugar de eliminar
    showToast('La eliminación de contratos está deshabilitada. Use el módulo Personal Médico para mantener la consistencia de datos.', 'error');
    return;
}

// Función para confirmar la eliminación - DESHABILITADA
function confirmDeleteContrato(idHospital, idPersonal) {
    showToast('La eliminación de contratos está deshabilitada. Use el módulo Personal Médico para mantener la consistencia de datos.', 'error');
    return;
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
