#!/bin/sh
set -e

# ─── Esperar MySQL si aplica ──────────────────────────────────────────────────
if [ "${DATABASE_URL#*mysql}" != "$DATABASE_URL" ]; then
    echo "MySQL DATABASE_URL detectado, esperando disponibilidad..."
    python - <<PY
import os, time, socket, urllib.parse
url = os.environ.get('DATABASE_URL', '')
try:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or 'db'
    port = parsed.port or 3306
except Exception:
    host = os.environ.get('DB_HOST', 'db')
    port = int(os.environ.get('DB_PORT', '3306'))

sock = socket.socket()
while True:
    try:
        sock.connect((host, port))
        sock.close()
        break
    except Exception:
        print('Esperando DB en %s:%s ...' % (host, port))
        time.sleep(1)
print('DB lista.')
PY
fi

# ─── Parche de esquema: agregar columnas faltantes de forma segura ─────────────
# Esto maneja el caso donde el DB ya existe con tablas antiguas (sin role/is_active).
python - <<'PY'
import os
from sqlalchemy import create_engine, text, inspect

url = os.environ.get('DATABASE_URL', 'sqlite:///asadero.db')
print(f"Verificando esquema en: {url.split('?')[0]}")

try:
    if url.startswith('sqlite'):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(url)

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if 'user' in tables:
        cols = [c['name'] for c in inspector.get_columns('user')]
        with engine.begin() as conn:
            dialect = engine.dialect.name
            if 'role' not in cols:
                print("  -> Agregando columna 'role' a tabla user...")
                conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
                print("     OK")
            if 'is_active' not in cols:
                print("  -> Agregando columna 'is_active' a tabla user...")
                if dialect == 'sqlite':
                    conn.execute(text("ALTER TABLE user ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
                else:
                    conn.execute(text("ALTER TABLE user ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"))
                print("     OK")
    else:
        print("  Tabla 'user' no existe aún, las migraciones la crearán.")

except Exception as e:
    print(f"  Advertencia en parche de esquema: {e}")
PY

# ─── Ejecutar migraciones Alembic ─────────────────────────────────────────────
if command -v flask >/dev/null 2>&1; then
    echo "Ejecutando migraciones..."

    # Si el DB tiene tablas pero no tiene alembic_version,
    # fue creado por db.create_all() directamente → sellar en head.
    python - <<'PY'
import os, sys
from sqlalchemy import create_engine, inspect

url = os.environ.get('DATABASE_URL', 'sqlite:///asadero.db')
try:
    if url.startswith('sqlite'):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(url)
    tables = inspect(engine).get_table_names()
    if tables and 'alembic_version' not in tables:
        print("DB sin control de migraciones detectado → se sellará en head.")
        sys.exit(1)
except Exception as e:
    print(f"Advertencia: {e}")
sys.exit(0)
PY
    UNMANAGED=$?

    # Intentar upgrade normal (falla silenciosamente si ya existe sin alembic_version)
    flask db upgrade 2>&1 || true

    # Si el DB estaba sin control de versiones, sellar en head ahora
    if [ "$UNMANAGED" = "1" ]; then
        echo "Sellando DB en versión actual de migraciones..."
        flask db stamp head 2>&1 || true
    fi

    echo "Migraciones completadas."
fi

# ─── Iniciar aplicación ───────────────────────────────────────────────────────
exec "$@"
