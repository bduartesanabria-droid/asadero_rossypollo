#!/usr/bin/env python
"""
Script principal para ejecutar la aplicación Flask
"""
import os
from app import create_app

if __name__ == '__main__':
    # Determinar configuración
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )
