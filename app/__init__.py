from dotenv import load_dotenv
load_dotenv()  # Must run before Config class is evaluated below

from flask import Flask
import os
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.exc import SQLAlchemyError
from app.config import config
from app.models import db, User

mail = Mail()

def create_app(config_name='development'):

    app = Flask(__name__)

    # Cargar configuración
    app.config.from_object(config[config_name])

    # ProxyFix: necesario para que Flask conozca HTTPS cuando está detrás de Traefik/nginx
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Inicializar extensiones
    db.init_app(app)
    mail.init_app(app)

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

    # Country flag images — maps team name to PNG filename in /static/img/flags/
    COUNTRY_FLAG_FILES = {
        'México': 'Mexico', 'Sudáfrica': 'Sudafrica', 'Corea del Sur': 'Corea_del_Sur',
        'Rep. Checa': 'Rep_Checa', 'Canadá': 'Canada', 'Bosnia y Herzegovina': 'Bosnia_y_Herzegovina',
        'Estados Unidos': 'Estados_Unidos', 'Paraguay': 'Paraguay', 'Qatar': 'Qatar',
        'Suiza': 'Suiza', 'Brasil': 'Brasil', 'Marruecos': 'Marruecos',
        'Haití': 'Haiti', 'Escocia': 'Escocia', 'Australia': 'Australia',
        'Turquía': 'Turquia', 'Alemania': 'Alemania', 'Curazao': 'Curazao',
        'Países Bajos': 'Paises_Bajos', 'Japón': 'Japon', 'Costa de Marfil': 'Costa_de_Marfil',
        'Ecuador': 'Ecuador', 'Suecia': 'Suecia', 'Túnez': 'Tunez',
        'España': 'Espana', 'Cabo Verde': 'Cabo_Verde', 'Bélgica': 'Belgica',
        'Egipto': 'Egipto', 'Arabia Saudí': 'Arabia_Saudi', 'Uruguay': 'Uruguay',
        'Irán': 'Iran', 'Nueva Zelanda': 'Nueva_Zelanda', 'Francia': 'Francia',
        'Senegal': 'Senegal', 'Irak': 'Irak', 'Noruega': 'Noruega',
        'Argentina': 'Argentina', 'Argelia': 'Argelia', 'Austria': 'Austria',
        'Jordania': 'Jordania', 'Portugal': 'Portugal', 'Rep. del Congo': 'Rep_del_Congo',
        'Inglaterra': 'Inglaterra', 'Croacia': 'Croacia', 'Ghana': 'Ghana',
        'Panamá': 'Panama', 'Uzbekistán': 'Uzbekistan', 'Colombia': 'Colombia',
    }

    @app.context_processor
    def inject_flags():
        from markupsafe import Markup
        def flag(team_name, size=24):
            filename = COUNTRY_FLAG_FILES.get(team_name)
            if not filename:
                return Markup('')
            h = int(size * 0.75)
            return Markup(
                f'<img src="/static/img/flags/{filename}.png" '
                f'alt="{team_name}" width="{size}" height="{h}" '
                f'style="border-radius:2px;vertical-align:middle;margin-right:4px;" '
                f'loading="lazy">'
            )
        return {'flag': flag}

    return app
