#!/bin/bash

echo "========================================"
echo "  VERDULERIA APP - INICIANDO SERVICIOS"
echo "========================================"
echo ""

# Verificar MySQL
echo "[1/4] Verificando MySQL..."
if ! systemctl is-active --quiet mysql; then
    echo "ADVERTENCIA: MySQL no está corriendo."
    echo "Ejecuta: sudo systemctl start mysql"
    echo ""
    read -p "Presiona Enter para continuar..."
fi

# Activar entorno virtual
echo "[2/4] Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: No se encuentra el entorno virtual."
    echo "Ejecuta: python3 -m venv venv"
    exit 1
fi

# Iniciar backend
echo "[3/4] Iniciando backend Flask en puerto 5000..."
gnome-terminal -- bash -c "echo 'Backend en http://127.0.0.1:5000'; python3 run.py; exec bash" &
sleep 3

# Iniciar frontend
echo "[4/4] Iniciando frontend en puerto 5500..."
gnome-terminal -- bash -c "cd frontend && echo 'Frontend en http://127.0.0.1:5500' && python3 -m http.server 5500; exec bash" &
sleep 2

# Abrir navegador
xdg-open http://127.0.0.1:5500

echo ""
echo "========================================"
echo "  SERVIDORES INICIADOS"
echo "========================================"
echo "Backend:  http://127.0.0.1:5000"
echo "Frontend: http://127.0.0.1:5500"
echo ""
echo "Credenciales de prueba:"
echo "  Admin:    admin@verduleria.local / admin123"
echo "  Empleado: empleado@verduleria.local / empleado123"
echo ""
echo "Cierra las terminales para detener los servidores."
echo ""