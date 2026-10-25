document.addEventListener('DOMContentLoaded', () => {
    const rol = getUserRol();
    const isAdmin = rol === 'admin';
    const isSupervisor = rol === 'supervisor';

    // Mostrar/ocultar botones según permisos
    if (isAdmin) {
        document.getElementById('btnNuevoEmpleado').style.display = 'inline-block';
    }

    // Cargar tabla inicial
    loadEmpleados();

    // Event Listeners de Modales
    document.getElementById('btnNuevoEmpleado').addEventListener('click', () => {
        document.getElementById('empleadoModalTitle').textContent = 'Nuevo Empleado';
        document.getElementById('empleadoForm').reset();
        document.getElementById('empleadoId').value = '';
        document.getElementById('empleadoModal').classList.add('show');
        document.getElementById('empleadoModal').style.display = 'block';
    });

    document.getElementById('btnCancelarEmpleado').addEventListener('click', closeModal);
    document.getElementById('empleadoForm').addEventListener('submit', handleEmpleadoSubmit);
});

function closeModal() {
    document.getElementById('empleadoModal').classList.remove('show');
    document.getElementById('empleadoModal').style.display = 'none';
}

async function loadEmpleados() {
    const tbody = document.querySelector('#empleadosTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</td></tr>';

    try {
        const result = await getEmpleados();
        tbody.innerHTML = '';
        const isAdmin = getUserRol() === 'admin';
        const isSupervisor = getUserRol() === 'supervisor';

        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No hay empleados registrados.</td></tr>';
            return;
        }

        result.data.forEach(emp => {
            const row = tbody.insertRow();
            
            // ID
            row.insertCell(0).innerHTML = `<span class="text-muted">#${emp.id}</span>`;
            
            // Nombre
            row.insertCell(1).innerHTML = `
                <div class="fw-bold">${emp.nombre} ${emp.apellido}</div>
                <div class="text-muted small">${emp.email}</div>
            `;
            
            // DNI
            row.insertCell(2).textContent = emp.dni;
            
            // Rol (Badge)
            const badgeClass = emp.rol === 'admin' ? 'badge-rol-admin' : (emp.rol === 'supervisor' ? 'badge-rol-supervisor' : 'badge-rol-empleado');
            row.insertCell(3).innerHTML = `<span class="badge rounded-pill ${badgeClass} text-capitalize">${emp.rol}</span>`;
            
            // Acciones
            const actions = row.insertCell(4);
            actions.className = 'acciones-btn';
            
            if (isAdmin || isSupervisor) {
                const editBtn = document.createElement('button');
                editBtn.className = 'btn btn-sm btn-outline-primary';
                editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
                editBtn.title = 'Editar';
                editBtn.onclick = () => editEmpleado(emp);
                actions.appendChild(editBtn);
            }
            
            if (isAdmin) {
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'btn btn-sm btn-outline-danger';
                deleteBtn.innerHTML = '<i class="bi bi-trash"></i>';
                deleteBtn.title = 'Dar de baja';
                deleteBtn.onclick = () => deleteEmpleado(emp.id);
                actions.appendChild(deleteBtn);

                const rolBtn = document.createElement('button');
                rolBtn.className = 'btn btn-sm btn-outline-warning';
                rolBtn.innerHTML = '<i class="bi bi-shield-lock"></i>';
                rolBtn.title = 'Cambiar Rol';
                rolBtn.onclick = () => changeRol(emp);
                actions.appendChild(rolBtn);
            }
        });
    } catch (error) {
        console.error('Error cargando empleados:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Error al cargar datos: ${error.message}</td></tr>`;
    }
}

function editEmpleado(emp) {
    document.getElementById('empleadoModalTitle').textContent = 'Editar Empleado';
    document.getElementById('empleadoId').value = emp.id;
    document.getElementById('empNombre').value = emp.nombre;
    document.getElementById('empApellido').value = emp.apellido;
    document.getElementById('empDni').value = emp.dni;
    document.getElementById('empEmail').value = emp.email;
    document.getElementById('empRol').value = emp.rol;
    
    document.getElementById('empleadoModal').classList.add('show');
    document.getElementById('empleadoModal').style.display = 'block';
}

async function deleteEmpleado(id) {
    if (confirm('¿Está seguro de dar de baja a este empleado? (Baja lógica)')) {
        try {
            await deleteEmpleadoAPI(id); // Asumiendo que así se llama en api.js
            loadEmpleados();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function changeRol(emp) {
    const newRol = prompt('Nuevo rol (admin/supervisor/empleado):', emp.rol);
    if (newRol && ['admin', 'supervisor', 'empleado'].includes(newRol)) {
        try {
            await updateRol(emp.id, newRol);
            loadEmpleados();
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
}

async function handleEmpleadoSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('empleadoId').value;
    const data = {
        nombre: document.getElementById('empNombre').value,
        apellido: document.getElementById('empApellido').value,
        dni: document.getElementById('empDni').value,
        email: document.getElementById('empEmail').value,
        rol: document.getElementById('empRol').value
    };

    try {
        if (id) {
            await updateEmpleado(id, data);
        } else {
            await createEmpleado(data);
        }
        closeModal();
        loadEmpleados();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}