from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from src.core.database import Database
import os

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    CORS(app)
    
    # Inicializar base de datos
    Database.init_db()
    
    # ============================================
    # RUTAS DEL FRONTEND
    # ============================================
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/<page>.html')
    def pages(page):
        try:
            return render_template(f'{page}.html')
        except:
            return render_template('index.html')
    
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory('../static/css', filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory('../static/js', filename)
    
    # ============================================
    # REGISTRAR MÓDULOS
    # ============================================
    from src.modules.auth_module.routes import auth_bp
    from src.modules.empleados_module.routes import empleados_bp
    from src.modules.asistencias_module.routes import asistencias_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(empleados_bp, url_prefix='/api/empleados')
    app.register_blueprint(asistencias_bp, url_prefix='/api/asistencias')
    
    return app