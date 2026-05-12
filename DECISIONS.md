# Decisiones técnicas - Verdulería App

## Metodología
Desarrollo en cascada adaptada (fases documentadas). Toma de decisiones registrada con fecha y justificación.

---

## 1. Arquitectura general (2025-05-08)

**Decisión:** Aplicación web en red local (sin nube), con API Flask servida desde PC de escritorio y clientes web en la misma red.

**Justificación:** Práctica de API-first, sin costos ni complejidad cloud. La próxima app implementará despliegue en nube.

**Alternativa descartada:** Uso de máquina virtual (se pospone para próximos proyectos pese a conocimiento previo de Linux).

---

## 2. Stack tecnológico (2025-05-08)

**Backend:** Python + Flask
**Razón:** Aprender Python, claridad en el código, buena documentación oficial.

**Base de datos:** MySQL Community Server
**Razón:** Relacional, maduro, compatible con Flask, práctica de SQL puro antes de ORM.

**Frontend (futuro):** HTML/CSS/JS vanilla (sin framework por ahora)
**Razón:** Enfocar energía en API y lógica de negocio primero.

**Alternativas descartadas:** Node.js (por priorizar aprendizaje de Python), PostgreSQL (MySQL es suficiente para alcance actual).

---

## 3. Modelo de datos (2025-05-08, actualizado 2025-05-12)

**Decisión:** Dos tablas relacionadas 1:N (personas → múltiples usuarios)

- `personas`: Datos personales, rol, estado activo, flag primer_login
- `usuarios`: Credenciales, password_hash, ultimo_login, auditoría

**Relación:** 1 persona puede tener N usuarios (ahora solo uno, futuro múltiples perfiles)

**Baja de empleados:** Lógica (campo `activo` en personas)
**Razón:** Conservar histórico de asistencias. Pendiente investigar implicaciones legales.

**Flag primer_login:** En tabla `personas` (no en usuarios)
**Razón:** El flag pertenece a la persona, no a una credencial específica. Si una persona tiene múltiples usuarios, todos comparten el mismo estado de primer login.

**password_hash:** En tabla `usuarios` (no en personas)
**Razón:** Una persona con múltiples usuarios tendría distintas contraseñas.

**Clave foránea:** `usuarios.persona_id → personas.id` con `ON DELETE CASCADE`
**Razón:** Si se borra una persona (baja física), se borran sus usuarios automáticamente.

**Auditoría:**
- `created_at`, `updated_at` en ambas tablas
- `ultimo_login` en tabla `usuarios`

---

## 4. Autenticación y seguridad (2025-05-08, actualizado 2025-05-12)

**Método:** JWT (JSON Web Tokens) stateless

**Manejo de primera contraseña:**
- Contraseña por defecto (ej: `cambiar123`)
- Forzar cambio en primer login mediante flag `primer_login` en personas
- Token especial para cambio de contraseña (más seguro que error HTTP)

**Flujo:**
1. Login con credenciales por defecto → backend detecta `primer_login=1`
2. Devuelve token especial (corto, solo para endpoint `/cambiar-password`)
3. Usuario cambia contraseña → `primer_login=0`
4. Devuelve token normal para uso general

**Protección en desarrollo (PC personal):**
- MySQL escuchando solo en 127.0.0.1 (bind-address)
- Usuario de BD `verduleria_app` con privilegios mínimos (SELECT, INSERT, UPDATE, DELETE)
- Variables de entorno para secretos (`.env` en .gitignore)
- Datos de prueba totalmente ficticios

**Alternativas descartadas:** Sesiones stateful (menos práctica para APIs)

---

## 5. Herramientas de desarrollo (2025-05-12)

**Editor:** VS Code

**Extensiones instaladas:**
- Python (Microsoft)
- Database Client JDBC y MySQL (cweijan)
- Black Formatter (formateo automático al guardar)

**Configuración Database Client:**
- SSL: Disabled (conexión local sin cifrado)
- Allow Public Key Retrieval: Yes (necesario para MySQL 8+)
- Puerto: 3306

**Formateador de código:** Black para Python

**Cliente de MySQL:** Database Client dentro de VS Code (evita cambiar de aplicación)

**Manejo de comandos Python/MySQL en Windows:**
- Uso de `py` en lugar de `python` o `pip` (el lanzador de Windows siempre disponible)

---

## 6. Desarrollo sin máquina virtual (2025-05-08)

**Decisión:** Desarrollar directamente en PC personal por ahora.

**Justificación:** PC dedicada a estudio (sin datos críticos), recursos limitados, conocimiento previo de Linux se aplicará en próxima app.

**Medidas compensatorias:**
- Datos de prueba ficticios
- MySQL aislado en puerto local
- `.env` fuera del repositorio
- Firewall personal activo

---

## 7. Entorno de desarrollo (2025-05-12)

**Estructura de carpetas:**
verduleria-api/
├── .env # Variables de entorno (no committear)
├── .gitignore
├── run.py # Punto de entrada (desde raíz)
├── src/
│ ├── app.py
│ ├── config/
│ │ └── db.py
│ ├── middleware/
│ ├── controllers/
│ └── routes/
├── sql/
│ └── schema.sql
└── docs/
├── README.md
├── DECISIONS.md
├── SECURITY.md
├── API_DOCS.md
└── TODO.md


**Ubicación de .env:** Raíz del proyecto (no dentro de venv/)

**Variables de entorno mínimas:**
DB_HOST=localhost
DB_USER=verduleria_app
DB_PASSWORD= (contraseña segura)
DB_NAME=verduleria_db
JWT_SECRET_KEY= (cadena aleatoria larga)
FLASK_SECRET_KEY= (otra cadena aleatoria)
PORT=5000

---

## 8. API Design (2025-05-12)

**Orden de implementación:**
1. POST /auth/login
2. POST /auth/cambiar-password
3. GET /empleados
4. POST /empleados
5. GET /empleados/{id}
6. PUT /empleados/{id}
7. PUT /empleados/{id}/rol (endpoint separado)
8. DELETE /empleados/{id}

**Respuesta GET /empleados:** Campos de personas + info de usuarios (ultimo_login)

**Rol cambiar:** Endpoint separado para mayor claridad de permisos

---

## Base de datos de ejemplo (2025-05-12)

**Decisión:** No instalar Sakila ni World.

**Justificación:** El proyecto construye su propio esquema (verduleria_db) desde cero.