import pytest

def test_login_exitoso_admin(client):
    """Test: Login de admin debe retornar token y rol admin"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['rol'] == 'admin'
    assert data['requires_change'] == False

def test_login_exitoso_empleado_primer_login(client):
    """Test: Login de empleado con primer_login=true debe devolver token especial"""
    response = client.post('/api/auth/login', json={
        'email': 'empleado@test.com',
        'password': 'empleado123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['requires_change'] == True
    assert data['message'] == 'Debe cambiar su contraseña'

def test_login_email_incorrecto(client):
    """Test: Login con email incorrecto debe retornar 401"""
    response = client.post('/api/auth/login', json={
        'email': 'noexiste@test.com',
        'password': 'cualquiercosa'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_login_password_incorrecto(client):
    """Test: Login con password incorrecto debe retornar 401"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password_incorrecta'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_login_faltan_datos(client):
    """Test: Login sin email o password debe retornar 400"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_login_sin_json(client):
    """Test: Login sin body JSON debe retornar 400 o 415"""
    response = client.post('/api/auth/login', data='texto plano')
    # Flask devuelve 415 cuando Content-Type no es application/json
    assert response.status_code in [400, 415]