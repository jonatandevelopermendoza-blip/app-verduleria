document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificar permisos (solo admin/supervisor)
    const rol = getUserRol();
    if (rol !== 'admin' && rol !== 'supervisor') {
        window.location.href = '/dashboard.html';
        return;
    }

    // 2. Cargar select de empleados
    loadEmpleadosSelect();

    // 3. Carga inicial de la tabla
    loadReporte();

    // 4. Event Listeners
    document.getElementById('filtrarBtn').addEventListener('click', () => {
        const fechaDesde = document.getElementById('fechaDesde').value;
        const fechaHasta = document.getElementById('fechaHasta').value;
        const empleadoId = document.getElementById('empleadoId').value;
        loadReporte(fechaDesde, fechaHasta, empleadoId);
    });

    document.getElementById('limpiarBtn').addEventListener('click', () => {
        document.getElementById('fechaDesde').value = '';
        document.getElementById('fechaHasta').value = '';
        document.getElementById('empleadoId').value = '';
        loadReporte();
    });
});

async function loadEmpleadosSelect() {
    try {
        const result = await getEmpleados();
        const select = document.getElementById('empleadoId');
        result.data.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = `${emp.nombre} ${emp.apellido}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando empleados:', error);
    }
}

async function loadReporte(fechaDesde = '', fechaHasta = '', empleadoId = '') {
    const tbody = document.querySelector('#reporteTable tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</td></tr>';

    try {
        const result = await getReporteAsistencias(fechaDesde, fechaHasta, empleadoId);
        tbody.innerHTML = '';
        
        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4"><i class="bi bi-inbox fs-3 d-block mb-2"></i>No hay registros en este período.</td></tr>';
            return;
        }

        result.data.forEach(a => {
            const row = tbody.insertRow();
            
            // Empleado
            row.insertCell(0).innerHTML = `<span class="fw-bold">${a.nombre} ${a.apellido}</span>`;
            
            // Fecha
            row.insertCell(1).textContent = a.fecha;
            
            // Entrada
            row.insertCell(2).innerHTML = a.hora_entrada ? `<span class="text-success fw-bold">${a.hora_entrada}</span>` : '-';
            
            // Salida
            row.insertCell(3).innerHTML = a.hora_salida ? `<span class="text-danger fw-bold">${a.hora_salida}</span>` : '-';
            
            // Horas (calculadas si existen ambas)
            let horas = '-';
            if (a.hora_entrada && a.hora_salida) {
                const entrada = new Date(`2000-01-01T${a.hora_entrada}`);
                const salida = new Date(`2000-01-01T${a.hora_salida}`);
                const diff = (salida - entrada) / (1000 * 3600);
                if (!isNaN(diff)) {
                    horas = `${diff.toFixed(1)} hs`;
                }
            }
            row.insertCell(4).textContent = horas;
            
            // Estado
            const estadoClase = a.estado === 'presente' ? 'bg-success' : (a.estado === 'ausente' ? 'bg-danger' : 'bg-warning text-dark');
            row.insertCell(5).innerHTML = `<span class="badge rounded-pill ${estadoClase} text-uppercase">${a.estado}</span>`;
        });
    } catch (error) {
        console.error('Error cargando reporte:', error);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger">Error al cargar datos: ${error.message}</td></tr>`;
    }
}