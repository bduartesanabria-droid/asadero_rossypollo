from dotenv import load_dotenv
load_dotenv()  # Must run before Config class is evaluated below

from flask import Flask
import os
from flask_login import LoginManager
from sqlalchemy.exc import SQLAlchemyError
from app.config import config
from app.models import db, User

def create_app(config_name='development'):

    app = Flask(__name__)

    # Cargar configuración
    app.config.from_object(config[config_name])

    # ProxyFix: necesario para que Flask conozca HTTPS cuando está detrás de Traefik/nginx
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

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
        return db.session.get(User, int(user_id))

    # Crear tablas (si no existen) + admin por defecto
    with app.app_context():
        db.create_all()
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
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Auto-transition matches from 'scheduled' → 'live' when their time passes
    @app.before_request
    def auto_update_match_status():
        from flask import request as req
        if req.path.startswith('/static') or req.path == '/service-worker.js':
            return
        from datetime import datetime
        from app.models import Match
        try:
            now = datetime.now()
            due = Match.query.filter(
                Match.status == 'scheduled',
                Match.match_date <= now
            ).all()
            if due:
                for m in due:
                    m.status = 'live'
                db.session.commit()
        except Exception:
            db.session.rollback()

    # Country flag emoji context processor — use {{ flag('México') }} in templates
    COUNTRY_FLAGS = {
        'México': '🇲🇽', 'Sudáfrica': '🇿🇦', 'Corea del Sur': '🇰🇷',
        'Rep. Checa': '🇨🇿', 'Canadá': '🇨🇦', 'Bosnia y Herzegovina': '🇧🇦',
        'Estados Unidos': '🇺🇸', 'Paraguay': '🇵🇾', 'Qatar': '🇶🇦',
        'Suiza': '🇨🇭', 'Brasil': '🇧🇷', 'Marruecos': '🇲🇦',
        'Haití': '🇭🇹', 'Escocia': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Australia': '🇦🇺',
        'Turquía': '🇹🇷', 'Alemania': '🇩🇪', 'Curazao': '🇨🇼',
        'Países Bajos': '🇳🇱', 'Japón': '🇯🇵', 'Costa de Marfil': '🇨🇮',
        'Ecuador': '🇪🇨', 'Suecia': '🇸🇪', 'Túnez': '🇹🇳',
        'España': '🇪🇸', 'Cabo Verde': '🇨🇻', 'Bélgica': '🇧🇪',
        'Egipto': '🇪🇬', 'Arabia Saudí': '🇸🇦', 'Uruguay': '🇺🇾',
        'Irán': '🇮🇷', 'Nueva Zelanda': '🇳🇿', 'Francia': '🇫🇷',
        'Senegal': '🇸🇳', 'Irak': '🇮🇶', 'Noruega': '🇳🇴',
        'Argentina': '🇦🇷', 'Argelia': '🇩🇿', 'Austria': '🇦🇹',
        'Jordania': '🇯🇴', 'Portugal': '🇵🇹', 'Rep. del Congo': '🇨🇩',
        'Inglaterra': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Croacia': '🇭🇷', 'Ghana': '🇬🇭',
        'Panamá': '🇵🇦', 'Uzbekistán': '🇺🇿', 'Colombia': '🇨🇴',
    }

    @app.context_processor
    def inject_flags():
        def flag(team_name):
            return COUNTRY_FLAGS.get(team_name, '')
        return {'flag': flag}

    return app
