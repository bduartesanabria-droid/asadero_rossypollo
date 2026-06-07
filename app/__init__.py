from flask import Flask
from flask_login import LoginManager
from app.config import config
from app.models import db, User

def create_app(config_name='development'):
    """Factory pattern para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints (rutas)
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
