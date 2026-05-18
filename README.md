# Verdulería App - Sistema de Administración de Empleados

## Descripción
Sistema completo para gestión de empleados de una verdulería. Incluye autenticación JWT, control de asistencias, CRUD de empleados y reportes.

## Tecnologías
- **Backend:** Flask (Python)
- **Base de datos:** MySQL
- **Frontend:** HTML, CSS, JavaScript vanilla
- **Autenticación:** JWT

## Requisitos previos
- Python 3.10 o superior
- MySQL Community Server
- Git (opcional)

## Instalación rápida (Windows)

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual**
   ```bash
   py -m venv venv
Activar entorno virtual

bash
venv\Scripts\activate
Instalar dependencias

bash
py -m pip install -r requirements.txt
Configurar MySQL

Crear base de datos: CREATE DATABASE verduleria_db;

Ejecutar sql/schema.sql

Crear usuario: verduleria_app con permisos sobre la BD

Configurar variables de entorno

Copiar .env.example a .env

Completar con tus valores (DB_PASSWORD, JWT_SECRET_KEY, etc.)

Iniciar la aplicación

Doble clic en iniciar.bat

O ejecutar: py run.py (backend) y cd frontend && py -m http.server 5500 (frontend)

Abrir navegador en http://127.0.0.1:5500

Credenciales de prueba
Rol	Email	Contraseña
Admin	admin@verduleria.local	admin123
Empleado	empleado@verduleria.local	empleado123
Funcionalidades
Login con JWT

Cambio obligatorio de contraseña en primer login

CRUD completo de empleados (con roles)

Registro de entrada/salida

Reporte de asistencias con filtros

Documentación adicional
API_DOCS.md - Endpoints y ejemplos

DECISIONS.md - Decisiones técnicas

SECURITY.md - Medidas de seguridad

Próximas mejoras (v2.0)
Exportar reportes a Excel/PDF

Notificaciones por email

Dashboard con gráficos

Modo oscuro

Aplicación móvil

Licencia
Proyecto educativo


---

