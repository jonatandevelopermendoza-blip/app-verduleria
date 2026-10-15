const rol = getUserRol();
        let asistenciasChart = null;
        let rolesChart = null;
        let horasChart = null;
        
        // Mostrar enlace de reporte solo para admin/supervisor
        if (rol === 'admin' || rol === 'supervisor') {
            document.getElementById('reporteLink').style.display = 'inline';
            document.getElementById('reporteLink').href = '/reporte.html';
        }
        
        document.getElementById('userRol').textContent = rol;
        document.getElementById('userName').textContent = localStorage.getItem('userName') || 'Empleado';
        
        // Cargar estadísticas
        async function loadStats() {
            try {
                // Resumen de empleados
                const empResponse = await apiRequest('/dashboard/empleados');
                const statsDiv = document.getElementById('statsContainer');
                statsDiv.innerHTML = `
                    <div class="stat-card">
                        <h4>Empleados Activos</h4>
                        <h3>${empResponse.data.activos}</h3>
                    </div>
                    <div class="stat-card">
                        <h4>Empleados Inactivos</h4>
                        <h3>${empResponse.data.inactivos}</h3>
                    </div>
                `;
                
                // Gráfico de roles
                const roles = empResponse.data.roles;
                if (rolesChart) rolesChart.destroy();
                const ctxRoles = document.getElementById('rolesChart').getContext('2d');
                rolesChart = new Chart(ctxRoles, {
                    type: 'pie',
                    data: {
                        labels: roles.map(r => r.rol),
                        datasets: [{
                            data: roles.map(r => r.cantidad),
                            backgroundColor: ['#e74c3c', '#f39c12', '#3498db']
                        }]
                    }
                });
                
                // Resumen de asistencias (últimos 7 días)
                const asisResponse = await apiRequest('/dashboard/resumen');
                if (asistenciasChart) asistenciasChart.destroy();
                const ctxAsis = document.getElementById('asistenciasChart').getContext('2d');
                asistenciasChart = new Chart(ctxAsis, {
                    type: 'line',
                    data: {
                        labels: asisResponse.data.fechas,
                        datasets: [
                            {
                                label: 'Entradas',
                                data: asisResponse.data.entradas,
                                borderColor: '#27ae60',
                                fill: false
                            },
                            {
                                label: 'Salidas',
                                data: asisResponse.data.salidas,
                                borderColor: '#e74c3c',
                                fill: false
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true
                    }
                });
                
                // Horas trabajadas (últimos 30 días)
                const horasResponse = await apiRequest('/dashboard/horas');
                if (horasChart) horasChart.destroy();
                const ctxHoras = document.getElementById('horasChart').getContext('2d');
                horasChart = new Chart(ctxHoras, {
                    type: 'bar',
                    data: {
                        labels: horasResponse.data.fechas,
                        datasets: [{
                            label: 'Horas trabajadas',
                            data: horasResponse.data.horas,
                            backgroundColor: '#3498db'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `${context.raw} horas`;
                                    }
                                }
                            }
                        }
                    }
                });
                
                // Mostrar total de horas
                const totalHoras = horasResponse.data.total_horas;
                statsDiv.innerHTML += `
                    <div class="stat-card">
                        <h4>Horas (último mes)</h4>
                        <h3>${totalHoras}</h3>
                    </div>
                `;
                
            } catch (error) {
                console.error('Error cargando estadísticas:', error);
            }
        }
        
        // Registrar asistencia
        document.getElementById('registrarBtn').addEventListener('click', async () => {
            const msgDiv = document.getElementById('mensaje');
            try {
                const result = await registrarAsistencia();
                msgDiv.className = 'alert success';
                msgDiv.textContent = result.message;
                msgDiv.style.display = 'block';
                setTimeout(() => msgDiv.style.display = 'none', 3000);
                // Recargar gráficos
                loadStats();
            } catch (error) {
                msgDiv.className = 'alert error';
                msgDiv.textContent = error.message;
                msgDiv.style.display = 'block';
                setTimeout(() => msgDiv.style.display = 'none', 3000);
            }
        });
        
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
        
        // Inicializar
        loadStats();
    