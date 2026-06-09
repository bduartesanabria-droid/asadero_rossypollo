#!/usr/bin/env python
"""
Script principal para ejecutar la aplicación Flask
"""
import os
from app import create_app

# Crear la app en tiempo de import para que gunicorn pueda cargar `run:app`
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Ejecutar servidor de desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )
