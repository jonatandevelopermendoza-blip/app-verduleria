// Manejo del formulario de login
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Verificar si ya hay sesión activa
    const token = sessionStorage.getItem('token');
    if (token && window.location.pathname.includes('index.html')) {
        window.location.href = 'dashboard.html';
    }
});

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('error');
    
    try {
        const result = await login(email, password);
        
        if (result.requires_change) {
            // Guardar token temporal y redirigir
            sessionStorage.setItem('temp_token', result.token);
            sessionStorage.removeItem('token');
            window.location.href = '/cambiar-password.html';
        } else {
            window.location.href = '/dashboard.html';
        }
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}