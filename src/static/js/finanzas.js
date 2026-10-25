let gastosChart = null;
let ingresosEgresosChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // Manejo del selector de período
    document.getElementById('periodo').addEventListener('change', (e) => {
        const esPersonalizado = e.target.value === 'personalizado';
        document.getElementById('fechaInicio').style.display = esPersonalizado ? 'block' : 'none';
        document.getElementById('fechaFin').style.display = esPersonalizado ? 'block' : 'none';
    });

    // Botones
    document.getElementById('btnFiltrar').addEventListener('click', loadResumen);
    
    // Modal de Gastos
    document.getElementById('btnNuevoGasto').addEventListener('click', () => {
        document.getElementById('gastoForm').reset();
        document.getElementById('gastoFecha').value = new Date().toISOString().split('T')[0];
        document.getElementById('gastoModal').classList.add('show');
        document.getElementById('gastoModal').style.display = 'block';
    });

    document.getElementById('btnCancelarGasto').addEventListener('click', () => {
        document.getElementById('gastoModal').classList.remove('show');
        document.getElementById('gastoModal').style.display = 'none';
    });

    document.getElementById('gastoForm').addEventListener('submit', handleGastoSubmit);

    // Carga inicial
    loadResumen();
    loadGastos();
});

async function loadResumen() {
    let periodo = document.getElementById('periodo').value;
    let url = '/finanzas/resumen?';
    
    if (periodo === 'personalizado') {
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;
        if (!fechaInicio || !fechaFin) {
            alert('Seleccione fechas de inicio y fin');
            return;
        }
        url += `fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`;
    } else {
        url += `periodo=${periodo}`;
    }
    
    try {
        const result = await apiRequest(url);
        const data = result.data;
        
        // Llenar tarjetas
        document.getElementById('valIngresos').textContent = `$${data.ingresos.bruto.toFixed(2)}`;
        document.getElementById('valIngresosNeto').textContent = `Neto: $${data.ingresos.neto.toFixed(2)} | IVA: $${data.ingresos.iva.toFixed(2)}`;
        
        document.getElementById('valEgresos').textContent = `$${data.egresos.total.toFixed(2)}`;
        document.getElementById('valEgresosDetalle').textContent = `Sueldos: $${data.egresos.sueldos.toFixed(2)} | Compras: $${data.egresos.compras_proveedores.toFixed(2)}`;
        
        document.getElementById('valBalance').textContent = `$${data.balance.toFixed(2)}`;
        document.getElementById('valMargen').textContent = `Margen: ${data.margen_ganancia}%`;
        
        // Gráfico de Gastos (Doughnut)
        const categorias = data.egresos.detalle_gastos || [];
        if (gastosChart) gastosChart.destroy();
        gastosChart = new Chart(document.getElementById('gastosChart'), {
            type: 'doughnut',
            data: {
                labels: categorias.map(c => c.categoria),
                datasets: [{ 
                    data: categorias.map(c => c.total_gastos), 
                    backgroundColor: ['#0d6efd', '#dc3545', '#ffc107', '#198754', '#6c757d'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '70%', plugins: { legend: { position: 'bottom' } }, maintainAspectRatio: false }
        });
        
        // Gráfico Ingresos vs Egresos (Bar)
        if (ingresosEgresosChart) ingresosEgresosChart.destroy();
        ingresosEgresosChart = new Chart(document.getElementById('ingresosEgresosChart'), {
            type: 'bar',
            data: {
                labels: ['Ingresos', 'Egresos'],
                datasets: [{ 
                    data: [data.ingresos.bruto, data.egresos.total], 
                    backgroundColor: ['#198754', '#dc3545'],
                    borderRadius: 5
                }]
            },
            options: { 
                plugins: { legend: { display: false } },
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true } }
            }
        });
        
    } catch (error) {
        console.error('Error cargando resumen:', error);
    }
}

async function loadGastos() {
    const tbody = document.querySelector('#gastosTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</td></tr>';

    try {
        const result = await apiRequest('/finanzas/gastos');
        tbody.innerHTML = '';
        const rol = getUserRol();

        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No hay gastos registrados.</td></tr>';
            return;
        }

        result.data.forEach(g => {
            const row = tbody.insertRow();
            row.insertCell(0).textContent = g.fecha;
            row.insertCell(1).innerHTML = `<span class="fw-bold">${g.concepto}</span>`;
            row.insertCell(2).innerHTML = `<span class="badge bg-secondary text-capitalize">${g.categoria}</span>`;
            row.insertCell(3).innerHTML = `<span class="text-danger fw-bold">-$${g.monto}</span>`;
            
            const actions = row.insertCell(4);
            if (rol === 'admin') {
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-sm btn-outline-danger';
                deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
                deleteBtn.onclick = () => eliminarGasto(g.id);
                actions.appendChild(deleteBtn);
            } else {
                actions.textContent = '-';
            }
        });
    } catch (error) {
        console.error('Error cargando gastos:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al cargar datos.</td></tr>`;
    }
}

async function eliminarGasto(id) {
    if (confirm('¿Eliminar este gasto?')) {
        try {
            await apiRequest(`/finanzas/gastos/${id}`, 'DELETE');
            loadGastos();
            loadResumen();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function handleGastoSubmit(e) {
    e.preventDefault();
    const data = {
        concepto: document.getElementById('gastoConcepto').value,
        descripcion: document.getElementById('gastoDescripcion').value,
        monto: parseFloat(document.getElementById('gastoMonto').value),
        fecha: document.getElementById('gastoFecha').value,
        categoria: document.getElementById('gastoCategoria').value,
        comprobante: document.getElementById('gastoComprobante').value
    };
    
    try {
        await apiRequest('/finanzas/gastos', 'POST', data);
        document.getElementById('gastoModal').classList.remove('show');
        document.getElementById('gastoModal').style.display = 'none';
        loadGastos();
        loadResumen();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}