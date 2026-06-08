import pytest
from datetime import date

def test_registrar_asistencia_sin_token(client):
    """Test: POST /asistencias/registrar sin token debe retornar 401"""
    response = client.post('/api/asistencias/registrar')
    assert response.status_code == 401

def test_registrar_entrada(client, auth_token):
    """Test: Registrar entrada debe ser exitoso"""
    response = client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'Entrada registrada' in data['message']

def test_registrar_salida(client, auth_token):
    """Test: Registrar salida después de entrada debe ser exitoso"""
    # Primera vez: entrada
    client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    # Segunda vez: salida
    response = client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'Salida registrada' in data['message']

def test_registrar_tercera_vez(client, auth_token):
    """Test: Tercer registro el mismo día debe dar error"""
    # Entrada
    client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    # Salida
    client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    # Tercero
    response = client.post('/api/asistencias/registrar',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_mis_asistencias(client, auth_token):
    """Test: GET /asistencias/mis-asistencias debe retornar listado"""
    response = client.get('/api/asistencias/mis-asistencias',
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert isinstance(data['data'], list)