from flask import Flask
from dotenv import load_dotenv
import os
from flask_cors import CORS  # <-- NUEVO
   

# Cargar variables de entorno desde .env
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuraciones desde .env
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    app.config['PORT'] = os.getenv('PORT', 5000)
    
    from src.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from src.routes.empleados_routes import empleados_bp
    app.register_blueprint(empleados_bp, url_prefix='/api/empleados')
    
    from src.routes.asistencias_routes import asistencias_bp
    app.register_blueprint(asistencias_bp, url_prefix='/api/asistencias')

    @app.route('/health', methods=['GET'])
    def health():
        """Endpoint de prueba para verificar que Flask corre"""
        return {"status": "ok", "message": "API funcionando"}
    
    @app.route('/test-db', methods=['GET'])
    def test_db():
        from src.config.db import Database
        try:
            result = Database.execute_query("SELECT 1 as test", fetch_one=True)
            return {"status": "ok", "db_connection": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    return app

# Para ejecutar directamente (debug)
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)