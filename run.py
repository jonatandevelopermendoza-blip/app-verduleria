from src.core.app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=False para distribución, True para desarrollo
    app.run(host='127.0.0.1', port=5000, debug=True)
import os
import sys
import webbrowser
import threading
import time

# Agregar la ruta actual al PATH para que encuentre los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.app import create_app

def open_browser():
    """Abre el navegador después de que el servidor esté listo"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    app = create_app()
    
    # Abrir navegador automáticamente (solo en ejecutable)
    if getattr(sys, 'frozen', False):
        threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='127.0.0.1', port=5000, debug=False)