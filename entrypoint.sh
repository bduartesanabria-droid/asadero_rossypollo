#!/bin/sh
set -e

echo "Ejecutando migraciones..."
flask db upgrade
echo "Migraciones completadas."

exec "$@"
