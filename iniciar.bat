@echo off
title Verdulería App - Servidor

echo ========================================
echo   VERDULERIA APP - INICIANDO SERVICIOS
echo ========================================
echo.

REM Verificar que MySQL esté corriendo
echo [1/4] Verificando MySQL...
sc query MySQL80 | find "RUNNING" > nul
if %errorlevel% neq 0 (
    echo ADVERTENCIA: MySQL no parece estar corriendo.
    echo Asegurate de iniciar MySQL antes de continuar.
    echo.
    pause
)

REM Activar entorno virtual
echo [2/4] Activando entorno virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se encuentra el entorno virtual.
    echo Ejecuta: py -m venv venv
    pause
    exit /b
)

REM Iniciar backend Flask
echo [3/4] Iniciando backend Flask en puerto 5000...
start "Flask Backend" cmd /k "echo Backend corriendo en http://127.0.0.1:5000 && py run.py"

REM Esperar a que Flask arranque
timeout /t 3 /nobreak > nul

REM Iniciar frontend
echo [4/4] Iniciando frontend en puerto 5500...
start "Frontend" cmd /k "cd frontend && echo Frontend corriendo en http://127.0.0.1:5500 && py -m http.server 5500"

REM Abrir navegador
timeout /t 2 /nobreak > nul
start http://127.0.0.1:5500

echo.
echo ========================================
echo   SERVIDORES INICIADOS
echo ========================================
echo Backend:  http://127.0.0.1:5000
echo Frontend: http://127.0.0.1:5500
echo.
echo Credenciales de prueba:
echo   Admin:    admin@verduleria.local / admin123
echo   Empleado: empleado@verduleria.local / empleado123
echo.
echo Cierra las ventanas negras para detener los servidores.
echo.
pause