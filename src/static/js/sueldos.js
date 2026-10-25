document.addEventListener('DOMContentLoaded', () => {
    const rol = getUserRol();
    // Verificar permisos (solo admin/supervisor)
    if (rol !== 'admin' && rol !== 'supervisor') {
        window.location.href = '/dashboard.html';
        return;
    }

    // Inicializar selectores de año y mes
    initSelectores();

    // Event Listeners
    document.getElementById('btnCalcular').addEventListener('click', calcularSueldos);
    document.getElementById('btnDescargar').addEventListener('click', descargarReporte);
});

function initSelectores() {
    const anioSelect = document.getElementById('anioSueldo');
    const mesSelect = document.getElementById('mesSueldo');
    const añoActual = new Date().getFullYear();
    
    anioSelect.innerHTML = '';
    for (let año = añoActual - 2; año <= añoActual + 1; año++) {
        anioSelect.innerHTML += `<option value="${año}">${año}</option>`;
    }
    anioSelect.value = añoActual;
    
    const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    mesSelect.innerHTML = meses.map((m, i) => `<option value="${i+1}">${m}</option>`).join('');
    mesSelect.value = new Date().getMonth() + 1;
}

async function calcularSueldos() {
    const anio = parseInt(document.getElementById('anioSueldo').value);
    const mes = parseInt(document.getElementById('mesSueldo').value);
    const btn = document.getElementById('btnCalcular');
    const resultadosDiv = document.getElementById('resultados');
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculando...';
    resultadosDiv.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary"></div><p class="mt-3 text-muted">Procesando sueldos...</p></div>';
    
    try {
        const result = await apiRequest('/sueldos/calcular', 'POST', { anio, mes });
        const data = result.data;
        
        let html = `
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="mb-0">Resultados - Período: ${data.periodo}</h4>
                <span class="badge bg-primary fs-6">${data.totales.empleados} empleados</span>
            </div>
            <div class="row g-3">
        `;
        
        data.empleados.forEach(e => {
            html += `
                <div class="col-md-6 col-lg-4">
                    <div class="sueldo-card h-100">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <span class="empleado">${e.nombre} ${e.apellido}</span>
                        </div>
                        <div class="text-muted small mb-2">
                            <i class="bi bi-clock me-1"></i> ${e.horas_trabajadas} hs trabajadas 
                            ${e.horas_extra > 0 ? `<span class="text-warning fw-bold">(+${e.horas_extra} extra)</span>` : ''}
                        </div>
                        <div class="d-flex justify-content-between mb-1">
                            <span class="small">Sueldo Base:</span>
                            <span>$${e.sueldo_base}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span class="small">Pago Extra:</span>
                            <span>$${e.pago_extra}</span>
                        </div>
                        <div class="d-flex justify-content-between pt-2 border-top">
                            <span class="fw-bold">Total:</span>
                            <span class="total">$${e.total_pagado}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
            </div>
            <div class="totales-box mt-4 d-flex justify-content-between align-items-center">
                <h5 class="mb-0 fw-bold">Total a pagar en el período:</h5>
                <h3 class="mb-0 text-success fw-bold">$${data.totales.total_sueldos}</h3>
            </div>
        `;
        
        resultadosDiv.innerHTML = html;
        
    } catch (error) {
        console.error('Error calculando sueldos:', error);
        resultadosDiv.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-calculator me-2"></i>Calcular Sueldos';
    }
}
async function descargarReporte(formato) {
    const anio = document.getElementById('anioSueldo').value;
    const mes = document.getElementById('mesSueldo').value.padStart(2, '0');
    const periodo = `${anio}-${mes}`;
    
    // Mostrar feedback (opcional)
    const btn = document.querySelector('.dropdown-toggle');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generando...';
    btn.disabled = true;

    try {
        const token = sessionStorage.getItem('token');
        const response = await fetch(`/api/sueldos/reporte?periodo=${periodo}&formato=${formato}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al descargar el reporte');
        }

        // Convertir la respuesta a un archivo Blob
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Crear un enlace invisible y hacer clic en él para descargar
        const a = document.createElement('a');
        a.href = url;
        
        // Obtener el nombre del archivo del header (opcional, pero más limpio)
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `sueldos_${periodo}.${formato}`;
        if (contentDisposition && contentDisposition.includes('filename=')) {
            filename = contentDisposition.split('filename=')[1].replace(/"/g, '');
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}