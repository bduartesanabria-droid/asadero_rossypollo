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
    role = db.Column(db.String(20), default='user', nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    results = db.relationship('Result', backref='user', lazy=True, cascade='all, delete-orphan')
    rankings = db.relationship('Ranking', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100), nullable=False)
    away_team = db.Column(db.String(100), nullable=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled', nullable=False)
    group = db.Column(db.String(20), nullable=True)

    @property
    def is_locked(self):
        from datetime import datetime
        return datetime.utcnow() >= self.match_date

    @property
    def result(self):
        if self.home_score is None or self.away_score is None:
            return None
        return f"{self.home_score} - {self.away_score}"

class Prediction(db.Model):
    __tablename__ = 'predictions'
    __table_args__ = (
        db.UniqueConstraint('match_id', 'predicted_home_score', 'predicted_away_score', name='unique_match_score'),
        db.UniqueConstraint('user_id', 'match_id', name='unique_user_match'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    predicted_home_score = db.Column(db.Integer, nullable=False)
    predicted_away_score = db.Column(db.Integer, nullable=False)
    points_earned = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('predictions', lazy=True))
    match = db.relationship('Match', backref=db.backref('predictions', lazy=True))

    def calculate_points(self):
        if self.match.home_score is None or self.match.away_score is None:
            return None

        actual_diff = self.match.home_score - self.match.away_score
        predicted_diff = self.predicted_home_score - self.predicted_away_score

        exact = (self.predicted_home_score == self.match.home_score and
                 self.predicted_away_score == self.match.away_score)
        same_outcome = (
            (actual_diff == 0 and predicted_diff == 0) or
            (actual_diff > 0 and predicted_diff > 0) or
            (actual_diff < 0 and predicted_diff < 0)
        )

        if exact:
            self.points_earned = 3
        elif same_outcome:
            self.points_earned = 1
        else:
            self.points_earned = 0

        return self.points_earned

class Ranking(db.Model):
    __tablename__ = 'rankings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Ranking user={self.user.username} points={self.points}>'

class Prize(db.Model):
    __tablename__ = 'prizes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    phase = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prize {self.name} ({self.phase})>'

class Category(db.Model):
    """Modelo de categorías para los posts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'
