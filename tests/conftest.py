import pytest
import tempfile
import os
import sqlite3
import shutil
import src.core.database as db_module
from src.core.app import create_app

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, 'sql', 'schema_sqlite.sql')

@pytest.fixture
def app():
    """Fixture que crea una app de prueba con base de datos temporal"""
    # Crear directorio temporal para la base de datos
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    # Guardar la ruta original y sobrescribir
    original_db_path = db_module.DB_PATH
    db_module.DB_PATH = db_path
    
    # Crear esquema en la base de datos temporal
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    # Crear la app
    app = create_app()
    app.config['TESTING'] = True
    
    # Insertar datos de prueba
    with app.app_context():
        seed_test_data()
    
    yield app
    
    # Limpiar
    db_module.DB_PATH = original_db_path
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def client(app):
    """Fixture que proporciona un cliente de prueba"""
    return app.test_client()

@pytest.fixture
def auth_token(client):
    """Fixture que obtiene un token de autenticación para admin"""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    if response.status_code != 200:
        return None
    data = response.get_json()
    return data.get('token') if data else None

def seed_test_data():
    """Carga datos de prueba en la base de datos temporal"""
    from src.core.database import Database
    import bcrypt
    
    admin_hash = bcrypt.hashpw(b'admin123', bcrypt.gensalt(10)).decode('utf-8')
    empleado_hash = bcrypt.hashpw(b'empleado123', bcrypt.gensalt(10)).decode('utf-8')
    
    conn = Database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Admin', 'Test', '11111111A', 'admin@test.com', 'admin', 1, 0))
    
    admin_id = cursor.lastrowid
    
    cursor.execute(
        "INSERT INTO usuarios (persona_id, password_hash) VALUES (?, ?)",
        (admin_id, admin_hash)
    )
    
    cursor.execute("""
        INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('Empleado', 'Test', '22222222B', 'empleado@test.com', 'empleado', 1, 1))
    
    emp_id = cursor.lastrowid
    
    cursor.execute(
        "INSERT INTO usuarios (persona_id, password_hash) VALUES (?, ?)",
        (emp_id, empleado_hash)
    )
    
    conn.commit()
    conn.close()