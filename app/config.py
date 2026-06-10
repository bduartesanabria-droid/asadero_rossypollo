import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a170ca4e261bd0e9525a9e94ffbcc15e50cba9b101180d2c39d52ec8054978aa')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///instance/asadero.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
