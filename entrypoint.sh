#!/bin/sh
set -e

# Esperar a que la base de datos esté lista (si se usa MySQL)
if [ "$FLASK_ENV" = "production" ]; then
  echo "Entorno producción: ejecutando migraciones si es necesario"
  if [ ! -d "migrations" ]; then
    flask db init || true
    flask db migrate -m "initial" || true
    flask db upgrade || true
  else
    flask db upgrade || true
  fi
fi

# Ejecutar el comando pasado al contenedor (por ejemplo gunicorn)
exec "$@"
