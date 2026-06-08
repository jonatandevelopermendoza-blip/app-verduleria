## PENDIENTE - Rate limiting

### Objetivo
Limitar intentos de login a 5 por minuto por IP.

### Implementación futura
1. Instalar flask-limiter
2. Configurar en app.py
3. Aplicar decorador @limiter.limit("5 per minute") a la ruta /login
4. Probar con 6 intentos fallidos

### Estado
⏳ Pospuesto - Se implementará después de funcionalidades core