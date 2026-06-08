// Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Función genérica para peticiones fetch
async function apiRequest(endpoint, method = 'GET', data = null, requiresAuth = true) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (requiresAuth) {
        const token = sessionStorage.getItem('token');
        if (!token) {
            window.location.href = 'index.html';
            throw new Error('No autenticado');
        }
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method: method,
        headers: headers
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, config);
        const result = await response.json();
        
        if (!response.ok) {
            if (response.status === 401) {
                sessionStorage.clear();
                window.location.href = 'index.html';
            }
            throw new Error(result.error || 'Error en la petición');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Funciones específicas de autenticación
async function login(email, password) {
    const result = await apiRequest('/auth/login', 'POST', { email, password }, false);
    if (result.token) {
        sessionStorage.setItem('token', result.token);
        sessionStorage.setItem('rol', result.rol);
        sessionStorage.setItem('requires_change', result.requires_change);
        return result;
    }
    throw new Error('Login fallido');
}

function logout() {
    sessionStorage.clear();
    window.location.href = 'index.html';
}

function getToken() {
    return sessionStorage.getItem('token');
}

function getUserRol() {
    return sessionStorage.getItem('rol');
}

// Funciones de empleados
async function getEmpleados() {
    return await apiRequest('/empleados/');
}

async function getEmpleado(id) {
    return await apiRequest(`/empleados/${id}`);
}

async function createEmpleado(empleado) {
    return await apiRequest('/empleados/', 'POST', empleado);
}

async function updateEmpleado(id, data) {
    return await apiRequest(`/empleados/${id}`, 'PUT', data);
}

async function updateRol(id, rol) {
    return await apiRequest(`/empleados/${id}/rol`, 'PUT', { rol });
}

async function deleteEmpleado(id) {
    return await apiRequest(`/empleados/${id}`, 'DELETE');
}

// Funciones de asistencias
async function registrarAsistencia() {
    return await apiRequest('/asistencias/registrar', 'POST');
}

async function getMisAsistencias(fechaDesde = '', fechaHasta = '') {
    let url = '/asistencias/mis-asistencias';
    const params = [];
    if (fechaDesde) params.push(`fecha_desde=${fechaDesde}`);
    if (fechaHasta) params.push(`fecha_hasta=${fechaHasta}`);
    if (params.length) url += '?' + params.join('&');
    return await apiRequest(url);
}

async function getReporteAsistencias(fechaDesde = '', fechaHasta = '', empleadoId = '') {
    let url = '/asistencias/reporte';
    const params = [];
    if (fechaDesde) params.push(`fecha_desde=${fechaDesde}`);
    if (fechaHasta) params.push(`fecha_hasta=${fechaHasta}`);
    if (empleadoId) params.push(`empleado_id=${empleadoId}`);
    if (params.length) url += '?' + params.join('&');
    return await apiRequest(url);
}