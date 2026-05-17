import bcrypt
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Datos de prueba
empleados_prueba = [
    {
        "nombre": "Admin",
        "apellido": "Principal",
        "dni": "11111111A",
        "email": "admin@verduleria.local",
        "rol": "admin",
        "activo": 1,
        "primer_login": 0,  # No necesita cambiar contraseña
        "password": "admin123"
    },
    {
        "nombre": "Empleado",
        "apellido": "Prueba",
        "dni": "22222222B",
        "email": "empleado@verduleria.local",
        "rol": "empleado",
        "activo": 1,
        "primer_login": 1,  # Debe cambiar contraseña al primer login
        "password": "empleado123"
    }
]

from src.controllers.auth_controller import hash_password

def insertar_datos():
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            for emp in empleados_prueba:
                # Insertar en personas
                sql_personas = """
                    INSERT INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_personas, (
                    emp["nombre"], emp["apellido"], emp["dni"], 
                    emp["email"], emp["rol"], emp["activo"], emp["primer_login"]
                ))
                
                # Obtener el ID generado
                persona_id = cursor.lastrowid
                
                # Insertar en usuarios con contraseña hasheada
                password_hash = hash_password(emp["password"])
                sql_usuarios = """
                    INSERT INTO usuarios (persona_id, password_hash, ultimo_login)
                    VALUES (%s, %s, NULL)
                """
                cursor.execute(sql_usuarios, (persona_id, password_hash))
            
            connection.commit()
            print(f"✅ Insertados {len(empleados_prueba)} empleados con sus usuarios")
            
            # Verificar
            cursor.execute("SELECT COUNT(*) as total FROM personas")
            total_personas = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            total_usuarios = cursor.fetchone()
            print(f"📊 Personas: {total_personas['total']}, Usuarios: {total_usuarios['total']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    insertar_datos()