# Guía de instalación - Verdulería App

## Windows

### 1. Instalar Python
- Descargar de python.org
- Marcar "Add Python to PATH"

### 2. Instalar MySQL
- Descargar MySQL Installer
- Elegir "Developer Default"
- Recordar la contraseña de root

### 3. Clonar el proyecto
```bash
git clone <tu-repo>
cd verduleria-api
4. Crear entorno virtual
bash
py -m venv venv
venv\Scripts\activate
5. Instalar dependencias
bash
py -m pip install -r requirements.txt
6. Configurar base de datos
Abrir MySQL Command Line Client

Ejecutar:

sql
CREATE DATABASE verduleria_db;
CREATE USER 'verduleria_app'@'localhost' IDENTIFIED BY 'tu_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON verduleria_db.* TO 'verduleria_app'@'localhost';
FLUSH PRIVILEGES;
USE verduleria_db;
SOURCE sql/schema.sql;
7. Configurar .env
bash
copy .env.example .env
Editar .env con tu contraseña de MySQL y claves secretas

8. Cargar datos de prueba
bash
py seed_data.py
9. Iniciar la app
bash
iniciar.bat
