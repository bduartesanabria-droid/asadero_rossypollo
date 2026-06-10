#!/bin/sh
set -e

# If DATABASE_URL points to MySQL, wait until the DB is reachable
if [ "${DATABASE_URL#*mysql}" != "$DATABASE_URL" ]; then
	echo "Detected MySQL DATABASE_URL, waiting for DB to become available..."
	python - <<PY
import os, time, socket, urllib.parse
url = os.environ.get('DATABASE_URL') or ''
try:
		parsed = urllib.parse.urlparse(url)
		host = parsed.hostname or 'db'
		port = parsed.port or 3306
except Exception:
		host = os.environ.get('DB_HOST','db')
		port = int(os.environ.get('DB_PORT','3306'))

sock = socket.socket()
while True:
		try:
				sock.connect((host, port))
				sock.close()
				break
		except Exception:
				print('Waiting for DB at %s:%s' % (host, port))
				time.sleep(1)
print('DB reachable')
PY
fi

# Apply migrations for all DB types (SQLite and MySQL/Postgres)
if command -v flask >/dev/null 2>&1; then
	echo "Running database migrations..."
	flask db upgrade || true
fi

exec "$@"
