// Verificar que hay un token de cambio
        const token = sessionStorage.getItem('token');
        const tempToken = sessionStorage.getItem('temp_token');
        
        if (!token && !tempToken) {
            window.location.href = '/';
        }
        
        // Usar el token disponible (priorizar temp_token si existe)
        const authToken = tempToken || token;
        
        document.getElementById('cambiarPasswordForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const nuevaPassword = document.getElementById('nueva_password').value;
            const confirmarPassword = document.getElementById('confirmar_password').value;
            const errorDiv = document.getElementById('error');
            const successDiv = document.getElementById('success');
            
            // Limpiar mensajes anteriores
            errorDiv.style.display = 'none';
            successDiv.style.display = 'none';
            
            // Validaciones
            if (nuevaPassword.length < 6) {
                errorDiv.textContent = 'La contraseña debe tener al menos 6 caracteres';
                errorDiv.style.display = 'block';
                return;
            }
            
            if (nuevaPassword !== confirmarPassword) {
                errorDiv.textContent = 'Las contraseñas no coinciden';
                errorDiv.style.display = 'block';
                return;
            }
            
            try {
                const response = await fetch('/api/auth/cambiar-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({ nueva_password: nuevaPassword })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Guardar el nuevo token normal
                    sessionStorage.setItem('token', data.token);
                    sessionStorage.removeItem('temp_token');
                    sessionStorage.setItem('rol', data.rol || 'empleado');
                    sessionStorage.setItem('requires_change', 'false');
                    
                    successDiv.textContent = 'Contraseña cambiada exitosamente. Redirigiendo...';
                    successDiv.style.display = 'block';
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard.html';
                    }, 1500);
                } else {
                    errorDiv.textContent = data.error || 'Error al cambiar la contraseña';
                    errorDiv.style.display = 'block';
                }
            } catch (error) {
                errorDiv.textContent = 'Error de conexión. Intente nuevamente.';
                errorDiv.style.display = 'block';
            }
        });