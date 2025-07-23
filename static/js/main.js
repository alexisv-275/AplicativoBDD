// JavaScript principal para el Sistema Hospitalario Distribuido

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    initializeTooltips();
    
    // Agregar animaciones de entrada
    addFadeInAnimations();
    
    // Inicializar funcionalidades específicas
    initializeFormValidations();
    initializeSearchFunctionality();
    
    // Configurar notificaciones
    setupNotifications();
    
    console.log('Sistema Hospitalario Distribuido - JavaScript cargado correctamente');
});

/**
 * Inicializar tooltips de Bootstrap
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Agregar animaciones de entrada a los elementos
 */
function addFadeInAnimations() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

/**
 * Validaciones de formularios
 */
function initializeFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Mostrar mensaje de error
                showNotification('Por favor, complete todos los campos requeridos.', 'warning');
            } else {
                // Mostrar indicador de carga
                showLoadingState(form);
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // Validación en tiempo real para cédula
    const cedulaInputs = document.querySelectorAll('input[name="cedula"]');
    cedulaInputs.forEach(input => {
        input.addEventListener('input', validateCedula);
        input.addEventListener('blur', validateCedula);
    });
    
    // Validación para emails
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', validateEmail);
    });
}

/**
 * Validar cédula ecuatoriana
 */
function validateCedula(event) {
    const input = event.target;
    const cedula = input.value;
    const isValid = isValidEcuadorianCedula(cedula);
    
    if (cedula.length === 10) {
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            
            // Mostrar información del nodo
            showNodeInfo(input, cedula);
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
            
            // Mostrar mensaje de error
            let feedback = input.parentNode.querySelector('.invalid-feedback');
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                input.parentNode.appendChild(feedback);
            }
            feedback.textContent = 'La cédula ingresada no es válida.';
        }
    } else if (cedula.length > 0) {
        input.classList.remove('is-valid', 'is-invalid');
    }
}

/**
 * Validar cédula ecuatoriana (algoritmo básico)
 */
function isValidEcuadorianCedula(cedula) {
    if (!/^\d{10}$/.test(cedula)) return false;
    
    const digits = cedula.split('').map(Number);
    const province = parseInt(cedula.substring(0, 2));
    
    // Verificar provincia válida (01-24)
    if (province < 1 || province > 24) return false;
    
    // Algoritmo de validación
    const coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    let sum = 0;
    
    for (let i = 0; i < 9; i++) {
        let result = digits[i] * coefficients[i];
        if (result > 9) result -= 9;
        sum += result;
    }
    
    const checkDigit = sum % 10 === 0 ? 0 : 10 - (sum % 10);
    return checkDigit === digits[9];
}

/**
 * Mostrar información del nodo según la cédula
 */
function showNodeInfo(input, cedula) {
    const nodoInfo = document.getElementById('nodoInfo');
    if (nodoInfo) {
        const isEven = parseInt(cedula) % 2 === 0;
        const node = isEven ? 'Quito' : 'Guayaquil';
        const color = isEven ? 'primary' : 'success';
        
        nodoInfo.innerHTML = `
            <div class="alert alert-${color} alert-sm">
                <i class="fas fa-server"></i> 
                Este paciente se almacenará en el nodo de <strong>${node}</strong>
            </div>
        `;
    }
}

/**
 * Validar email
 */
function validateEmail(event) {
    const input = event.target;
    const email = input.value;
    
    if (email.length > 0) {
        const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        
        if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
        }
    } else {
        input.classList.remove('is-valid', 'is-invalid');
    }
}

/**
 * Funcionalidad de búsqueda
 */
function initializeSearchFunctionality() {
    const searchInputs = document.querySelectorAll('input[placeholder*="Buscar"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('keyup', debounce(function() {
            performSearch(this);
        }, 300));
    });
}

/**
 * Realizar búsqueda en tabla
 */
function performSearch(input) {
    const filter = input.value.toUpperCase();
    const table = input.parentNode.querySelector('table') || 
                  input.closest('.card-body').querySelector('table');
    
    if (!table) return;
    
    const rows = table.getElementsByTagName('tr');
    let visibleRows = 0;
    
    for (let i = 1; i < rows.length; i++) {
        let found = false;
        const cells = rows[i].getElementsByTagName('td');
        
        for (let j = 0; j < cells.length - 1; j++) {
            if (cells[j].textContent.toUpperCase().indexOf(filter) > -1) {
                found = true;
                break;
            }
        }
        
        rows[i].style.display = found ? '' : 'none';
        if (found) visibleRows++;
    }
    
    // Mostrar mensaje si no hay resultados
    showSearchResults(table, visibleRows, filter);
}

/**
 * Mostrar resultados de búsqueda
 */
function showSearchResults(table, visibleRows, filter) {
    let noResultsRow = table.querySelector('.no-results-row');
    
    if (visibleRows === 0 && filter.length > 0) {
        if (!noResultsRow) {
            const tbody = table.querySelector('tbody');
            noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            noResultsRow.innerHTML = `
                <td colspan="100%" class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-2"></i>
                    <br>No se encontraron resultados para "${filter}"
                </td>
            `;
            tbody.appendChild(noResultsRow);
        }
        noResultsRow.style.display = '';
    } else if (noResultsRow) {
        noResultsRow.style.display = 'none';
    }
}

/**
 * Debounce function para optimizar búsquedas
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Estado de carga en formularios
 */
function showLoadingState(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            Procesando...
        `;
        submitBtn.disabled = true;
        
        // Restaurar estado después de 3 segundos (fallback)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 3000);
    }
}

/**
 * Sistema de notificaciones
 */
function setupNotifications() {
    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) return;
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            try {
                bsAlert.close();
            } catch (e) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

/**
 * Mostrar notificación temporal
 */
function showNotification(message, type = 'info', duration = 3000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remover después del tiempo especificado
    setTimeout(() => {
        try {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        } catch (e) {
            alertDiv.remove();
        }
    }, duration);
}

/**
 * Confirmar acciones peligrosas
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Formatear números para estadísticas
 */
function formatNumber(num) {
    return new Intl.NumberFormat('es-EC').format(num);
}

/**
 * Actualizar estadísticas en tiempo real (opcional)
 */
function updateStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            // Actualizar elementos de estadísticas
            const totalElement = document.querySelector('.stat-total');
            const quitoElement = document.querySelector('.stat-quito');
            const guayaquilElement = document.querySelector('.stat-guayaquil');
            
            if (totalElement) totalElement.textContent = formatNumber(data.total || 0);
            if (quitoElement) quitoElement.textContent = formatNumber(data.quito || 0);
            if (guayaquilElement) guayaquilElement.textContent = formatNumber(data.guayaquil || 0);
        })
        .catch(error => {
            console.error('Error actualizando estadísticas:', error);
        });
}

/**
 * Utilidades globales
 */
window.HospitalSystem = {
    showNotification,
    confirmAction,
    formatNumber,
    updateStats,
    validateCedula: isValidEcuadorianCedula
};
