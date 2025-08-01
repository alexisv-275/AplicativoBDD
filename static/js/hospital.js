// Hospital Dashboard - Cargar estadísticas dinámicas
document.addEventListener('DOMContentLoaded', function() {
    loadHospitalStats();
});

function loadHospitalStats() {
    console.log('🔄 Iniciando carga de estadísticas...');
    
    fetch('/api/hospital/stats')
        .then(response => {
            console.log('📡 Respuesta recibida:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📊 Datos recibidos:', data);
            
            if (data.success) {
                console.log('✅ Datos válidos, actualizando display...');
                updateStatsDisplay(data.stats);
                showSuccess('Estadísticas actualizadas correctamente');
            } else {
                console.error('❌ Error en respuesta:', data.error);
                showError('Error al cargar estadísticas: ' + data.error);
                setDefaultStats();
            }
        })
        .catch(error => {
            console.error('💥 Error completo:', error);
            showError('Error de conexión al cargar estadísticas');
            setDefaultStats();
        });
}

function updateStatsDisplay(stats) {
    console.log('🎯 Actualizando display con stats:', stats);
    
    // Actualizar estadísticas generales (parte superior)
    updateGeneralStats(stats);
    
    // Actualizar estadísticas por nodo
    updateNodeStats(stats);
    
    console.log('✅ Display actualizado');
}

function updateGeneralStats(stats) {
    console.log('📊 Actualizando estadísticas generales...');
    
    // Pacientes Activos
    const pacientesCard = document.querySelector('.col-md-3:nth-child(1) h4');
    if (pacientesCard) {
        pacientesCard.innerHTML = formatNumber(stats.total_pacientes);
    }
    
    // Citas 
    const citasCard = document.querySelector('.col-md-3:nth-child(2) h4');
    const citasLabel = document.querySelector('.col-md-3:nth-child(2) small');
    if (citasCard) {
        citasCard.innerHTML = formatNumber(stats.total_citas);
    }
    if (citasLabel) {
        citasLabel.textContent = 'Citas';
    }
    
    // Personal Médico
    const personalCard = document.querySelector('.col-md-3:nth-child(3) h4');
    if (personalCard) {
        personalCard.innerHTML = formatNumber(stats.total_personal);
    }
    
    // Especialidades
    const especialidadesCard = document.querySelector('.col-md-3:nth-child(4) h4');
    if (especialidadesCard) {
        especialidadesCard.innerHTML = formatNumber(stats.total_especialidades);
    }
}

function updateNodeStats(stats) {
    console.log('🎯 Actualizando estadísticas por nodo...');
    
    // Nodo Quito - buscar por el header con bg-success
    const quitoHeader = document.querySelector('.card-header.bg-success');
    if (quitoHeader) {
        const quitoCard = quitoHeader.closest('.card');
        const quitoStats = quitoCard.querySelector('.row.text-center');
        if (quitoStats) {
            const quitoCols = quitoStats.querySelectorAll('.col-4');
            if (quitoCols.length >= 3) {
                console.log('✅ Actualizando Quito:', stats.quito);
                // Pacientes
                quitoCols[0].querySelector('h4').innerHTML = formatNumber(stats.quito.pacientes);
                quitoCols[0].querySelector('small').textContent = 'Pacientes';
                
                // Citas
                quitoCols[1].querySelector('h4').innerHTML = formatNumber(stats.quito.citas);
                quitoCols[1].querySelector('small').textContent = 'Citas';
                
                // Personal Médico
                quitoCols[2].querySelector('h4').innerHTML = formatNumber(stats.quito.personal_medico);
                quitoCols[2].querySelector('small').textContent = 'Personal Médico';
            }
        }
    } else {
        console.error('❌ No se encontró el header de Quito (.card-header.bg-success)');
    }
    
    // Nodo Guayaquil - buscar por el header con bg-info
    const guayaquilHeader = document.querySelector('.card-header.bg-info');
    if (guayaquilHeader) {
        const guayaquilCard = guayaquilHeader.closest('.card');
        const guayaquilStats = guayaquilCard.querySelector('.row.text-center');
        if (guayaquilStats) {
            const guayaquilCols = guayaquilStats.querySelectorAll('.col-4');
            if (guayaquilCols.length >= 3) {
                console.log('✅ Actualizando Guayaquil:', stats.guayaquil);
                // Pacientes
                guayaquilCols[0].querySelector('h4').innerHTML = formatNumber(stats.guayaquil.pacientes);
                guayaquilCols[0].querySelector('small').textContent = 'Pacientes';
                
                // Citas
                guayaquilCols[1].querySelector('h4').innerHTML = formatNumber(stats.guayaquil.citas);
                guayaquilCols[1].querySelector('small').textContent = 'Citas';
                
                // Personal Médico
                guayaquilCols[2].querySelector('h4').innerHTML = formatNumber(stats.guayaquil.personal_medico);
                guayaquilCols[2].querySelector('small').textContent = 'Personal Médico';
            }
        }
    } else {
        console.error('❌ No se encontró el header de Guayaquil (.card-header.bg-info)');
    }
}

function setDefaultStats() {
    console.log('⚠️ Estableciendo valores por defecto...');
    // Establecer valores por defecto en caso de error (sin spinners)
    const defaultStats = {
        total_pacientes: '---',
        total_citas: '---',
        total_personal: '---',
        total_especialidades: '---',
        quito: {
            pacientes: '---',
            citas: '---',
            personal_medico: '---'
        },
        guayaquil: {
            pacientes: '---',
            citas: '---',
            personal_medico: '---'
        }
    };
    
    updateStatsDisplay(defaultStats);
}

function formatNumber(num) {
    // Formatear números con comas para miles
    return num.toLocaleString();
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
