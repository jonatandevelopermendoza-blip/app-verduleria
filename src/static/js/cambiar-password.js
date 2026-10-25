document.addEventListener('DOMContentLoaded', () => {
    // Verificar que el usuario tenga un token temporal o normal
    const token = sessionStorage.getItem('token');
    const tempToken = sessionStorage.getItem('temp_token');
    
    if (!token && !tempToken) {
        window.location.href = '/';
        return;
    }
    
    // Usar el token temporal si existe, sino el normal
    const authToken = tempToken || token;

    const form = document.getElementById('cambiarPasswordForm');
    const errorDiv = document.getElementById('error');
    const successDiv = document.getElementById('success');
    const btnSubmit = document.getElementById('btnSubmit');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nuevaPassword = document.getElementById('nueva_password').value;
        const confirmarPassword = document.getElementById('confirmar_password').value;
        
        errorDiv.classList.add('d-none');
        successDiv.classList.add('d-none');
        
        // Validaciones frontend
        if (nuevaPassword.length < 6) {
            errorDiv.textContent = 'La contraseña debe tener al menos 6 caracteres.';
            errorDiv.classList.remove('d-none');
            return;
        }
        
        if (nuevaPassword !== confirmarPassword) {
            errorDiv.textContent = 'Las contraseñas no coinciden.';
            errorDiv.classList.remove('d-none');
            return;
        }
        
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Actualizando...';
        
        try {
            // Llamada directa a la API
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
                // Guardar el nuevo token normal (ya no es token de cambio)
                sessionStorage.setItem('token', data.token);
                sessionStorage.setItem('rol', data.rol || 'empleado');
                sessionStorage.removeItem('temp_token');
                sessionStorage.setItem('requires_change', 'false');
                
                successDiv.innerHTML = '<i class="bi bi-check-circle me-2"></i>¡Contraseña actualizada! Redirigiendo...';
                successDiv.classList.remove('d-none');
                
                setTimeout(() => {
                    window.location.href = '/dashboard.html';
                }, 1500);
            } else {
                errorDiv.textContent = data.error || 'Error al cambiar la contraseña';
                errorDiv.classList.remove('d-none');
            }
        } catch (error) {
            errorDiv.textContent = 'Error de conexión. Intente nuevamente.';
            errorDiv.classList.remove('d-none');
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = 'Actualizar Contraseña <i class="bi bi-shield-check ms-2"></i>';
        }
    });
});