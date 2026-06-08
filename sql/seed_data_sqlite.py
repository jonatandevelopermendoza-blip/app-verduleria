import sqlite3
import bcrypt
import os

DB_PATH = 'verduleria.db'

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Datos de prueba
    empleados = [
        ('Admin', 'Principal', '11111111A', 'admin@verduleria.local', 'admin', 1, 0, hash_password('admin123')),
        ('Empleado', 'Prueba', '22222222B', 'empleado@verduleria.local', 'empleado', 1, 1, hash_password('empleado123')),
        ('Carlos', 'Lopez', '44444444D', 'carlos@verduleria.local', 'empleado', 1, 1, hash_password('cambiar123'))
    ]
    
    try:
        for emp in empleados:
            # Insertar persona
            cursor.execute('''
                INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6]))
            
            persona_id = cursor.lastrowid
            
            # Insertar usuario
            cursor.execute('''
                INSERT INTO usuarios (persona_id, password_hash, ultimo_login)
                VALUES (?, ?, NULL)
            ''', (persona_id, emp[7]))
        
        conn.commit()
        print(f"✅ Insertados {len(empleados)} empleados")
        
        # Verificar
        cursor.execute("SELECT COUNT(*) FROM personas")
        count = cursor.fetchone()[0]
        print(f"📊 Total personas: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()