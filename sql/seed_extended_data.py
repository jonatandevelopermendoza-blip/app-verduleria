import sqlite3
import bcrypt
import random
from datetime import datetime, timedelta
import os

DB_PATH = 'verduleria.db'

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')

def generate_asistencias(empleado_id, days_back=30):
    """Genera asistencias aleatorias para un empleado en los últimos N días"""
    asistencias = []
    hoy = datetime.now().date()
    
    for i in range(days_back):
        fecha = hoy - timedelta(days=i)
        # Evitar domingos (día 6 = domingo en Python)
        if fecha.weekday() == 6:  # Domingo
            continue
        
        # 90% de probabilidad de que haya asistencia
        if random.random() < 0.9:
            hora_entrada = f"{random.randint(8, 10)}:{random.randint(0, 59):02d}:00"
            hora_salida = f"{random.randint(17, 19)}:{random.randint(0, 59):02d}:00"
            asistencias.append((empleado_id, fecha.isoformat(), hora_entrada, hora_salida))
    
    return asistencias

def seed_extended_data():
    """Carga datos de prueba extendidos"""
    if not os.path.exists(DB_PATH):
        print("❌ Base de datos no encontrada. Ejecuta primero la app para crearla.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("📊 Cargando datos extendidos...")
    
    # Hash de contraseñas
    admin_hash = hash_password('admin123')
    empleado_hash = hash_password('empleado123')
    nuevo_hash = hash_password('cambiar123')
    
    # Empleados adicionales
    empleados = [
        ('Ana', 'García', '33333333C', 'ana@verduleria.local', 'supervisor', 1, 0, empleado_hash),
        ('Luis', 'Martínez', '44444444D', 'luis@verduleria.local', 'empleado', 1, 1, nuevo_hash),
        ('María', 'Rodríguez', '55555555E', 'maria@verduleria.local', 'empleado', 1, 1, nuevo_hash),
        ('Juan', 'Sánchez', '66666666F', 'juan@verduleria.local', 'empleado', 1, 1, nuevo_hash),
        ('Laura', 'Fernández', '77777777G', 'laura@verduleria.local', 'empleado', 1, 1, nuevo_hash),
        ('Pedro', 'Gómez', '88888888H', 'pedro@verduleria.local', 'empleado', 1, 1, nuevo_hash),
        ('Carmen', 'López', '99999999I', 'carmen@verduleria.local', 'supervisor', 1, 0, empleado_hash),
    ]
    
    # Insertar empleados
    for emp in empleados:
        cursor.execute("""
            INSERT OR IGNORE INTO personas (nombre, apellido, dni, email, rol, activo, primer_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6]))
        
        if cursor.lastrowid:
            cursor.execute(
                "INSERT INTO usuarios (persona_id, password_hash) VALUES (?, ?)",
                (cursor.lastrowid, emp[7])
            )
    
    # Obtener todos los empleados activos
    cursor.execute("SELECT id, nombre FROM personas WHERE activo = 1")
    empleados_ids = cursor.fetchall()
    
    print(f"📋 Empleados activos: {len(empleados_ids)}")
    
    # Generar asistencias para los últimos 30 días
    total_asistencias = 0
    for emp_id, nombre in empleados_ids:
        asistencias = generate_asistencias(emp_id, 30)
        for a in asistencias:
            cursor.execute("""
                INSERT OR IGNORE INTO asistencias (persona_id, fecha, hora_entrada, hora_salida, estado)
                VALUES (?, ?, ?, ?, 'presente')
            """, a)
            if cursor.rowcount > 0:
                total_asistencias += 1
        print(f"  • {nombre}: {len(asistencias)} asistencias")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Datos cargados correctamente:")
    print(f"   - {len(empleados)} empleados")
    print(f"   - {total_asistencias} asistencias en los últimos 30 días")

if __name__ == "__main__":
    seed_extended_data()