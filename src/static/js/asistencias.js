const rol = getUserRol();
        if (rol === 'admin' || rol === 'supervisor') {
            document.getElementById('reporteLink').style.display = 'inline';
            document.getElementById('reporteLink').href = 'reporte.html';
        }
        
        async function loadAsistencias(fechaDesde = '', fechaHasta = '') {
            try {
                const result = await getMisAsistencias(fechaDesde, fechaHasta);
                const tbody = document.querySelector('#asistenciasTable tbody');
                tbody.innerHTML = '';
                result.data.forEach(a => {
                    const row = tbody.insertRow();
                    row.insertCell(0).textContent = a.fecha;
                    row.insertCell(1).textContent = a.hora_entrada || '-';
                    row.insertCell(2).textContent = a.hora_salida || '-';
                    let horas = '-';
                    if (a.hora_entrada && a.hora_salida) {
                        const entrada = new Date(`2000-01-01T${a.hora_entrada}`);
                        const salida = new Date(`2000-01-01T${a.hora_salida}`);
                        const diff = (salida - entrada) / (1000 * 3600);
                        horas = diff.toFixed(1);
                    }
                    row.insertCell(3).textContent = horas;
                    row.insertCell(4).textContent = a.estado;
                });
            } catch (error) {
                console.error('Error cargando asistencias:', error);
            }
        }
        
        document.getElementById('registrarBtn').addEventListener('click', async () => {
            const msgDiv = document.getElementById('mensaje');
            try {
                const result = await registrarAsistencia();
                msgDiv.className = 'alert success';
                msgDiv.textContent = result.message;
                msgDiv.style.display = 'block';
                loadAsistencias();
                setTimeout(() => msgDiv.style.display = 'none', 3000);
            } catch (error) {
                msgDiv.className = 'alert error';
                msgDiv.textContent = error.message;
                msgDiv.style.display = 'block';
                setTimeout(() => msgDiv.style.display = 'none', 3000);
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
        
        document.getElementById('logoutBtn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
        
        loadAsistencias();
    