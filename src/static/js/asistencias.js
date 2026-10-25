document.addEventListener('DOMContentLoaded', () => {
    // 1. Configurar permisos del menú
    const rol = getUserRol();
    if (rol === 'admin' || rol === 'supervisor') {
        const reporteLink = document.getElementById('reporteLink');
        if (reporteLink) {
            reporteLink.style.display = 'inline';
            reporteLink.href = '/reporte.html';
        }
    }

    // 2. Cargar asistencias iniciales
    loadAsistencias();

    // 3. Event Listeners
    document.getElementById('registrarBtn').addEventListener('click', async () => {
        const msgDiv = document.getElementById('mensaje');
        const btn = document.getElementById('registrarBtn');
        
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';

        try {
            const result = await registrarAsistencia();
            msgDiv.className = 'alert alert-success shadow-sm';
            msgDiv.innerHTML = `<i class="bi bi-check-circle me-2"></i>${result.message}`;
            msgDiv.style.display = 'block';
            
            // Recargar tabla
            await loadAsistencias();
            
            setTimeout(() => msgDiv.style.display = 'none', 4000);
        } catch (error) {
            msgDiv.className = 'alert alert-danger shadow-sm';
            msgDiv.innerHTML = `<i class="bi bi-exclamation-triangle me-2"></i>${error.message}`;
            msgDiv.style.display = 'block';
            setTimeout(() => msgDiv.style.display = 'none', 4000);
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-fingerprint me-2"></i>Registrar Entrada/Salida';
        }
    });

    document.getElementById('filtrarBtn').addEventListener('click', () => {
        const fechaDesde = document.getElementById('fechaDesde').value;
        const fechaHasta = document.getElementById('fechaHasta').value;
        loadAsistencias(fechaDesde, fechaHasta);
    });

    document.getElementById('limpiarBtn').addEventListener('click', () => {
        document.getElementById('fechaDesde').value = '';
        document.getElementById('fechaHasta').value = '';
        loadAsistencias();
    });
});

async function loadAsistencias(fechaDesde = '', fechaHasta = '') {
    const tbody = document.querySelector('#asistenciasTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</td></tr>';

    try {
        const result = await getMisAsistencias(fechaDesde, fechaHasta);
        tbody.innerHTML = '';
        
        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4"><i class="bi bi-inbox fs-3 d-block mb-2"></i>No hay registros en este período</td></tr>';
            return;
        }

        result.data.forEach(a => {
            const row = tbody.insertRow();
            
            // Fecha
            row.insertCell(0).innerHTML = `<span class="fw-bold">${a.fecha}</span>`;
            
            // Entrada
            row.insertCell(1).innerHTML = a.hora_entrada ? `<span class="text-success fw-bold">${a.hora_entrada}</span>` : '-';
            
            // Salida
            row.insertCell(2).innerHTML = a.hora_salida ? `<span class="text-danger fw-bold">${a.hora_salida}</span>` : '-';
            
            // Horas
            let horas = '-';
            if (a.hora_entrada && a.hora_salida) {
                const entrada = new Date(`2000-01-01T${a.hora_entrada}`);
                const salida = new Date(`2000-01-01T${a.hora_salida}`);
                const diff = (salida - entrada) / (1000 * 3600);
                horas = `${diff.toFixed(1)} hs`;
            }
            row.insertCell(3).textContent = horas;
            
            // Estado
            const estadoClase = a.estado === 'presente' ? 'badge-presente' : (a.estado === 'ausente' ? 'badge-ausente' : 'badge-justificado');
            row.insertCell(4).innerHTML = `<span class="badge rounded-pill ${estadoClase}">${a.estado.toUpperCase()}</span>`;
        });
    } catch (error) {
        console.error('Error cargando asistencias:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al cargar datos: ${error.message}</td></tr>`;
    }
}