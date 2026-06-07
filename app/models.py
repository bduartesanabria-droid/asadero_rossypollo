from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuario"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con posts
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    # Relación con resultados
    results = db.relationship('Result', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Encripta la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    """Modelo de posts/artículos del blog"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    
    # Relaciones
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    
    # Metadatos
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    views = db.Column(db.Integer, default=0)
    
    # Relación con categoría
    category = db.relationship('Category', backref='posts')
    
    def __repr__(self):
        return f'<Post {self.title}>'

class Result(db.Model):
    """Modelo de resultados o registros de competencia"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event = db.Column(db.String(150), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    is_winner = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Result {self.event} - {self.user.username}>'

# Modelo de Polla - Partidos y Pronósticos
class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.DateTime, nullable=False)
    group = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='scheduled')

    @property
    def is_locked(self):
        from datetime import datetime
        return datetime.utcnow() >= self.match_date

class Prediction(db.Model):
    __tablename__ = 'prediction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    predicted_home_score = db.Column(db.Integer, nullable=False)
    predicted_away_score = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('predictions', lazy=True))
    match = db.relationship('Match', backref=db.backref('predictions', lazy=True))

    def calculate_points(self):
        if self.match.home_score is None or self.match.away_score is None:
            return None
        if (self.predicted_home_score == self.match.home_score and
                self.predicted_away_score == self.match.away_score):
            self.points_earned = 3
        elif ((self.predicted_home_score - self.predicted_away_score) *
              (self.match.home_score - self.match.away_score) > 0) or (
              self.predicted_home_score == self.predicted_away_score and
              self.match.home_score == self.match.away_score):
            self.points_earned = 1
        else:
            self.points_earned = 0
        return self.points_earned

class Category(db.Model):
    """Modelo de categorías para los posts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'
