# API de Administración de Empleados - Verdulería

## Información general

| Item | Descripción |
|------|-------------|
| **Base URL** | `http://127.0.0.1:5000/api` |
| **Formato** | JSON |
| **Versión** | 1.0.0 |

## Autenticación

La mayoría de los endpoints requieren un token JWT enviado en el header `Authorization`:

## Authorization: Bearer <token>

### Tipos de token

| Tipo | Duración | Uso |
|------|----------|-----|
| **Token normal** | 8 horas | Acceso a endpoints protegidos |
| **Token especial de cambio** | 15 minutos | Solo para cambiar contraseña (primer login) |

### Códigos de estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | Éxito (GET, PUT, DELETE) |
| 201 | Recurso creado (POST exitoso) |
| 400 | Error de validación |
| 401 | No autenticado (token faltante o inválido) |
| 403 | No autorizado (rol insuficiente o usuario inactivo) |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |

---

## Endpoints de Autenticación

### POST /auth/login

Inicia sesión y obtiene un token JWT.

**Request:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@verduleria.local",
  "password": "admin123"
}

### Respuestas:

200 OK (admin o empleado sin cambio requerido):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "requires_change": false,
  "rol": "admin",
  "message": "Login exitoso"
}

## 200 OK (empleado con primer_login = true):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "requires_change": true,
  "message": "Debe cambiar su contraseña"
}

401 Unauthorized:

json
{
  "error": "Credenciales inválidas"
}
403 Forbidden:

json
{
  "error": "Usuario dado de baja"
}
POST /auth/cambiar-password
Cambia la contraseña del usuario. Requiere token especial de cambio (el que se obtiene cuando requires_change = true).

Headers:

text
Authorization: Bearer <token_especial>
Request:

http
POST /api/auth/cambiar-password
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{
  "nueva_password": "nueva123"
}
Respuesta 200 OK:

json
{
  "message": "Contraseña actualizada correctamente",
  "token": "eyJhbGciOiJIUzI1NiIs... (nuevo token normal)"
}
Errores:

Código	Respuesta
400	{"error": "Nueva contraseña requerida"}
400	{"error": "La contraseña debe tener al menos 6 caracteres"}
401	{"error": "Token requerido"}
403	{"error": "Se requiere token especial de cambio de contraseña"}
Endpoints de Empleados
GET /empleados
Lista todos los empleados activos (baja lógica).
Requiere token. Cualquier rol autenticado.

Headers:

text
Authorization: Bearer <token>
Request:

http
GET /api/empleados/
Respuesta 200 OK:

json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "nombre": "Admin",
      "apellido": "Principal",
      "dni": "11111111A",
      "email": "admin@verduleria.local",
      "rol": "admin",
      "primer_login": false,
      "ultimo_login": "2026-05-14T10:41:13",
      "created_at": "2026-05-12T11:27:47",
      "updated_at": "2026-05-12T11:27:47"
    },
    {
      "id": 2,
      "nombre": "Empleado",
      "apellido": "Prueba",
      "dni": "22222222B",
      "email": "empleado@verduleria.local",
      "rol": "empleado",
      "primer_login": false,
      "ultimo_login": "2026-05-13T15:51:20",
      "created_at": "2026-05-12T11:27:47",
      "updated_at": "2026-05-13T15:50:23"
    }
  ]
}
Errores:

Código	Respuesta
401	{"error": "Token requerido"}
401	{"error": "Token inválido"}
401	{"error": "Token expirado"}
GET /empleados/{id}
Obtiene el detalle de un empleado específico.
Requiere token. Cualquier rol autenticado.

Headers:

text
Authorization: Bearer <token>
Request:

http
GET /api/empleados/1
Respuesta 200 OK:

json
{
  "success": true,
  "data": {
    "id": 1,
    "nombre": "Admin",
    "apellido": "Principal",
    "dni": "11111111A",
    "email": "admin@verduleria.local",
    "rol": "admin",
    "activo": true,
    "primer_login": false,
    "ultimo_login": "2026-05-14T10:41:13",
    "created_at": "2026-05-12T11:27:47",
    "updated_at": "2026-05-12T11:27:47"
  }
}
Error 404:

json
{
  "error": "Empleado no encontrado"
}
POST /empleados
Crea un nuevo empleado.
Requiere token. Solo rol admin.

Headers:

text
Authorization: Bearer <token_admin>
Content-Type: application/json
Request:

http
POST /api/empleados/
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{
  "nombre": "Carlos",
  "apellido": "Lopez",
  "dni": "44444444D",
  "email": "carlos@verduleria.local",
  "rol": "empleado"
}
Respuesta 201 Created:

json
{
  "success": true,
  "message": "Empleado creado correctamente",
  "id": 3
}
Errores:

Código	Respuesta
400	{"error": "Falta campo requerido: nombre"}
400	{"error": "Rol inválido. Debe ser: admin, supervisor o empleado"}
400	{"error": "El DNI o email ya existe"}
401	{"error": "Token requerido"}
403	{"error": "Permisos insuficientes"}
PUT /empleados/{id}
Actualiza datos de un empleado (nombre, apellido, dni, email).
Requiere token. Roles permitidos: admin o supervisor.

Headers:

text
Authorization: Bearer <token>
Content-Type: application/json
Request:

http
PUT /api/empleados/3
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{
  "nombre": "Carlos",
  "apellido": "Gomez",
  "email": "carlos.nuevo@verduleria.local"
}
Respuesta 200 OK:

json
{
  "success": true,
  "message": "Empleado actualizado correctamente"
}
Errores:

Código	Respuesta
400	{"error": "No hay campos para actualizar"}
404	{"error": "Empleado no encontrado"}
401	{"error": "Token requerido"}
403	{"error": "Permisos insuficientes"}
PUT /empleados/{id}/rol
Cambia el rol de un empleado.
Requiere token. Solo rol admin.

Headers:

text
Authorization: Bearer <token_admin>
Content-Type: application/json
Request:

http
PUT /api/empleados/3/rol
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

{
  "rol": "supervisor"
}
Respuesta 200 OK:

json
{
  "success": true,
  "message": "Rol actualizado a supervisor"
}
Errores:

Código	Respuesta
400	{"error": "Se requiere el campo 'rol'"}
400	{"error": "Rol inválido"}
404	{"error": "Empleado no encontrado"}
401	{"error": "Token requerido"}
403	{"error": "Permisos insuficientes"}
DELETE /empleados/{id}
Da de baja lógica a un empleado (cambia activo a false).
Requiere token. Solo rol admin.

Headers:

text
Authorization: Bearer <token_admin>
Request:

http
DELETE /api/empleados/3
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Respuesta 200 OK:

json
{
  "success": true,
  "message": "Empleado dado de baja correctamente"
}
Errores:

Código	Respuesta
404	{"error": "Empleado no encontrado"}
400	{"error": "El empleado ya está dado de baja"}
401	{"error": "Token requerido"}
403	{"error": "Permisos insuficientes"}
Ejemplos con cURL
1. Login como admin
bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@verduleria.local","password":"admin123"}'
2. Listar empleados (usando el token obtenido)
bash
curl -X GET http://127.0.0.1:5000/api/empleados/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
3. Crear nuevo empleado (como admin)
bash
curl -X POST http://127.0.0.1:5000/api/empleados/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -d '{"nombre":"Ana","apellido":"Perez","dni":"77777777G","email":"ana@verduleria.local","rol":"empleado"}'
4. Cambiar rol (como admin)
bash
curl -X PUT http://127.0.0.1:5000/api/empleados/3/rol \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -d '{"rol":"supervisor"}'
5. Dar de baja un empleado (como admin)
bash
curl -X DELETE http://127.0.0.1:5000/api/empleados/3 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
6. Login como empleado (primer login)
bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"empleado@verduleria.local","password":"empleado123"}'
7. Cambiar contraseña (usando token especial de la respuesta anterior)
bash
curl -X POST http://127.0.0.1:5000/api/auth/cambiar-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs... (token especial)" \
  -d '{"nueva_password":"nueva123"}'
Flujo completo de uso
Para un empleado nuevo (primer login)
Login con credenciales por defecto → recibe requires_change: true y token especial

Cambiar contraseña usando el token especial → recibe token normal

Login nuevamente con la nueva contraseña → recibe requires_change: false y token normal

Acceder a endpoints protegidos usando el token normal

Para un admin
Login con credenciales → recibe token normal

Acceder a todos los endpoints (incluyendo creación, cambio de roles, bajas)

Notas de seguridad
Los tokens JWT expiran automáticamente (8 horas para normales, 15 minutos para especiales)

Las contraseñas se almacenan hasheadas con bcrypt (costo 10)

Los empleados dados de baja no pueden iniciar sesión

Los roles limitan el acceso a endpoints específicos
