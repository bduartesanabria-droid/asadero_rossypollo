#!/usr/bin/env python
"""
Script principal para ejecutar la aplicación Flask
"""
import os
from app import create_app

# Usar FLASK_ENV para seleccionar la configuración correcta
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', 'True').lower() not in ('false', '0', 'no')
    app.run(host='0.0.0.0', port=5000, debug=debug)
