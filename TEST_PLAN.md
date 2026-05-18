# Plan de pruebas - Verdulería App

## Pruebas de autenticación
- [ ] Login con admin → token normal
- [ ] Login con empleado nuevo → token especial + requires_change=true
- [ ] Cambiar contraseña con token especial → éxito
- [ ] Cambiar contraseña con token normal → error 403
- [ ] Login con usuario inactivo → error 403

## Pruebas de empleados (como admin)
- [ ] Listar empleados → todos los activos
- [ ] Crear empleado → 201 Created
- [ ] Crear empleado con DNI duplicado → error 400
- [ ] Editar empleado → datos actualizados
- [ ] Cambiar rol → rol actualizado
- [ ] Eliminar empleado (baja lógica) → activo=false

## Pruebas de asistencias
- [ ] Registrar entrada → éxito con mensaje
- [ ] Registrar salida (mismo día) → éxito con mensaje
- [ ] Registrar tercer registro mismo día → error 400
- [ ] Ver mis asistencias → listado personal
- [ ] Reporte general (admin) → todos los registros

## Pruebas de seguridad
- [ ] Endpoint protegido sin token → 401
- [ ] Endpoint de admin con token de empleado → 403
- [ ] Token expirado → 401