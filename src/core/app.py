from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
#from flask_limiter import Limiter
#from flask_limiter.util import get_remote_address
from src.core.database import Database
import os

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    CORS(app)
    
    # Configurar rate limiter (sin asignarlo a app.extensions directamente)
    #limiter = Limiter(
    #    get_remote_address,
    #    app=app,
    #    default_limits=["200 per day", "50 per hour"],
    #    storage_uri="memory://"
    #)
    
    # Inicializar base de datos
    Database.init_db()
    
    # ============================================
    # RUTAS DEL FRONTEND (igual que antes)
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
    
    from src.modules.dashboard_module.routes import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    from src.modules.horarios_module.routes import horarios_bp
    from src.modules.stock_module.routes import stock_bp
    from src.modules.ventas_module.routes import ventas_bp

    app.register_blueprint(horarios_bp, url_prefix='/api/horarios')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(ventas_bp, url_prefix='/api/ventas')

    return app