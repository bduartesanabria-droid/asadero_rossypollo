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

	# Apply migrations if flask is available
	if command -v flask >/dev/null 2>&1; then
		echo "Running database migrations..."
		flask db upgrade || true
	fi
fi

	# Ensure schema compatibility for simple deployments: add missing `role` column if needed
	python - <<PY
	import os
	from sqlalchemy import create_engine, text
	url = os.environ.get('DATABASE_URL') or ''
	if url.startswith('sqlite'):
		engine = create_engine(url, connect_args={"check_same_thread": False})
	else:
		engine = create_engine(url)

	with engine.connect() as conn:
		try:
			dialect = engine.dialect.name
			if dialect == 'sqlite':
				res = conn.execute(text("PRAGMA table_info('user')"))
				cols = [r[1] for r in res.fetchall()]
				if 'role' not in cols:
					print('Adding role column to user table (sqlite)')
					conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
			else:
				# For MySQL/Postgres attempt safe add
				try:
					conn.execute(text("SELECT role FROM user LIMIT 1"))
				except Exception:
					print('Adding role column to user table (SQL)')
					if dialect == 'mysql':
						conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'"))
					else:
						conn.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'user'"))
		except Exception as e:
			print('Schema check/alter failed:', e)
	PY

	exec "$@"
