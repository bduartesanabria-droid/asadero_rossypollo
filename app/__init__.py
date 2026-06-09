from flask import Flask
import os
from flask_login import LoginManager
from sqlalchemy.exc import SQLAlchemyError
from app.config import config
from app.models import db, User

def create_app(config_name='development'):
    """Factory pattern para crear la aplicación Flask"""
    # Cargar variables de entorno desde .env
    from dotenv import load_dotenv
    load_dotenv()

    app = Flask(__name__)

    # Cargar configuración
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)

    # Inicializar migraciones
    from flask_migrate import Migrate
    migrate = Migrate(app, db)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Crear tablas solo en desarrollo (en producción usar migraciones)
    if config_name == 'development':
        with app.app_context():
            db.create_all()

    # Crear super admin si variables de entorno definidas
    with app.app_context():
        admin_username = os.getenv('ADMIN_USERNAME')
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_username and admin_email and admin_password:
            try:
                existing_admin = User.query.filter_by(username=admin_username).first()
            except SQLAlchemyError:
                existing_admin = None

            if not existing_admin:
                try:
                    admin_user = User(username=admin_username, email=admin_email, is_admin=True)
                    admin_user.set_password(admin_password)
                    db.session.add(admin_user)
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
    
    # Registrar blueprints (rutas)
    from app.routes import main_bp
    from app.auth_routes import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app
