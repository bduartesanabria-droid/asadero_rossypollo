#!/usr/bin/env python
"""
Script principal para ejecutar la aplicación Flask
"""
import os
from app import create_app

# Crear la app en tiempo de import para que gunicorn pueda cargar `run:app`
app = create_app('development')

if __name__ == '__main__':
    # Ejecutar servidor de desarrollo
    app.run(host='0.0.0.0', port=5000, debug=True)
