document.addEventListener('DOMContentLoaded', () => {
    const rol = getUserRol();
    const esAdminSupervisor = rol === 'admin' || rol === 'supervisor';

    // Mostrar sección de admin si corresponde
    if (esAdminSupervisor) {
        document.getElementById('adminHorariosSection').style.display = 'block';
        cargarEmpleadosSelect();
    }

    // Cargas iniciales
    cargarMiHorario();

    // Eventos de Admin
    if (esAdminSupervisor) {
        document.getElementById('empleadoHorario').addEventListener('change', cargarHorariosEmpleado);
        document.getElementById('asignarHorarioBtn').addEventListener('click', asignarHorario);
    }

    // Evento de Cálculo de Pago
    document.getElementById('calcularPagoBtn').addEventListener('click', calcularPago);
});

async function cargarMiHorario() {
    const container = document.getElementById('miHorario');
    container.innerHTML = '<div class="text-center py-3"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</div>';
    
    try {
        const result = await apiRequest('/horarios/');
        container.innerHTML = '';
        
        if (result.data.length === 0) {
            container.innerHTML = '<div class="alert alert-info mb-0">No hay horarios asignados aún.</div>';
            return;
        }

        result.data.forEach(h => {
            const div = document.createElement('div');
            div.className = 'horario-row';
            div.innerHTML = `
                <span class="dia-semana">${h.dia_semana}</span>
                <span>${h.hora_inicio} - ${h.hora_fin}</span>
                <span class="horas">${h.horas_esperadas} hs</span>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger mb-0">Error: ${error.message}</div>`;
    }
}

async function cargarEmpleadosSelect() {
    try {
        const result = await getEmpleados();
        const select = document.getElementById('empleadoHorario');
        select.innerHTML = '<option value="">Seleccione un empleado...</option>';
        
        result.data.forEach(emp => {
            select.innerHTML += `<option value="${emp.id}">${emp.nombre} ${emp.apellido} (${emp.rol})</option>`;
        });
    } catch (error) {
        console.error('Error cargando empleados:', error);
    }
}

async function cargarHorariosEmpleado() {
    const empleadoId = document.getElementById('empleadoHorario').value;
    const container = document.getElementById('horariosAsignados');
    
    if (!empleadoId) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = '<div class="text-center py-2"><span class="spinner-border spinner-border-sm"></span></div>';

    try {
        const result = await apiRequest(`/horarios/empleado/${empleadoId}`);
        container.innerHTML = '';
        
        if (result.data.length === 0) {
            container.innerHTML = '<p class="text-muted small">Este empleado no tiene horarios asignados.</p>';
            return;
        }

        result.data.forEach(h => {
            const div = document.createElement('div');
            div.className = 'horario-row bg-light mb-2 rounded';
            div.innerHTML = `
                <span class="dia-semana">${h.dia_semana}</span>
                <span>${h.hora_inicio} - ${h.hora_fin}</span>
                <span class="horas">${h.horas_esperadas} hs</span>
            `;
            container.appendChild(div);
        });
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger py-2">Error: ${error.message}</div>`;
    }
}

async function asignarHorario() {
    const empleadoId = document.getElementById('empleadoHorario').value;
    if (!empleadoId) {
        alert('Seleccione un empleado primero.');
        return;
    }

    const data = {
        persona_id: parseInt(empleadoId),
        dia_semana: document.getElementById('diaSemana').value,
        hora_inicio: document.getElementById('horaInicio').value,
        hora_fin: document.getElementById('horaFin').value,
        horas_esperadas: parseFloat(document.getElementById('horasEsperadas').value)
    };

    try {
        await apiRequest('/horarios/', 'POST', data);
        alert('Horario asignado correctamente');
        cargarHorariosEmpleado();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function calcularPago() {
    const anio = document.getElementById('anioPago').value;
    const mes = document.getElementById('mesPago').value;
    const sueldoBase = parseFloat(document.getElementById('sueldoBase').value);
    const valorHoraExtra = parseFloat(document.getElementById('valorHoraExtra').value);
    const resultadoDiv = document.getElementById('resultadoPago');

    resultadoDiv.innerHTML = '<div class="text-center"><span class="spinner-border spinner-border-sm me-2"></span>Calculando...</div>';

    try {
        const result = await apiRequest('/horarios/pago', 'POST', {
            anio: parseInt(anio),
            mes: parseInt(mes),
            sueldo_base: sueldoBase,
            valor_hora_extra: valorHoraExtra
        });
        
        const data = result.data;
        resultadoDiv.innerHTML = `
            <div class="resultado-pago">
                <h6 class="fw-bold mb-3">Resultado: ${data.periodo}</h6>
                <div class="d-flex justify-content-between mb-1">
                    <span>Horas trabajadas:</span> <strong>${data.horas_trabajadas} hs</strong>
                </div>
                <div class="d-flex justify-content-between mb-1">
                    <span>Horas esperadas:</span> <strong>${data.horas_esperadas} hs</strong>
                </div>
                <div class="d-flex justify-content-between mb-1 text-success">
                    <span>Horas extra:</span> <strong>${data.horas_extra} hs</strong>
                </div>
                <hr>
                <div class="d-flex justify-content-between mb-1">
                    <span>Sueldo base:</span> <span>$${data.sueldo_base}</span>
                </div>
                <div class="d-flex justify-content-between mb-1">
                    <span>Pago extra:</span> <span>$${data.pago_extra}</span>
                </div>
                <div class="d-flex justify-content-between mt-2 pt-2 border-top border-success">
                    <span class="fw-bold fs-5">Total a pagar:</span> 
                    <span class="fw-bold fs-5 text-success">$${data.total_pagado}</span>
                </div>
            </div>
        `;
    } catch (error) {
        resultadoDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}