import pytest

def test_listar_empleados_sin_token(client):
    """Test: GET /empleados sin token debe retornar 401"""
    # Asegurar que NO se envía token
    response = client.get('/api/empleados/')
    # Si devuelve 200, el endpoint no requiere autenticación
    assert response.status_code == 401, f"Esperaba 401, obtuve {response.status_code}"
    
def test_listar_empleados_con_token(client, auth_token):
    """Test: GET /empleados con token debe retornar lista"""
    response = client.get('/api/empleados/', headers={
        'Authorization': f'Bearer {auth_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 2  # Admin y empleado

def test_crear_empleado_como_admin(client, auth_token):
    """Test: POST /empleados como admin debe crear empleado"""
    response = client.post('/api/empleados/', 
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'nombre': 'Nuevo',
            'apellido': 'Test',
            'dni': '33333333C',
            'email': 'nuevo@test.com',
            'rol': 'empleado'
        }
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True
    assert 'id' in data

def test_crear_empleado_dni_duplicado(client, auth_token):
    """Test: POST con DNI duplicado debe retornar 400"""
    response = client.post('/api/empleados/', 
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'nombre': 'Otro',
            'apellido': 'Test',
            'dni': '11111111A',  # DNI ya existe (admin)
            'email': 'otro@test.com',
            'rol': 'empleado'
        }
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_crear_empleado_sin_rol(client, auth_token):
    """Test: POST sin campo rol debe retornar 400"""
    response = client.post('/api/empleados/', 
        headers={'Authorization': f'Bearer {auth_token}'},
        json={
            'nombre': 'Incompleto',
            'apellido': 'Test',
            'dni': '44444444D',
            'email': 'incompleto@test.com'
        }
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_obtener_empleado_por_id(client, auth_token):
    """Test: GET /empleados/{id} debe retornar datos del empleado"""
    response = client.get('/api/empleados/1', 
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert data['data']['id'] == 1
    assert data['data']['email'] == 'admin@test.com'

def test_obtener_empleado_inexistente(client, auth_token):
    """Test: GET /empleados/{id} con ID inexistente debe retornar 404"""
    response = client.get('/api/empleados/999', 
        headers={'Authorization': f'Bearer {auth_token}'})
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data