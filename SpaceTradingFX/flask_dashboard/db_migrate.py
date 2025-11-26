"""
Simple migration helper: adds `password_hash` and `is_admin` columns to `users` table
for SQLite databases created without those columns.

Run this from the project root (or inside venv) like:
  python SpaceTradingFX/flask_dashboard/db_migrate.py

It will inspect the configured `SQLALCHEMY_DATABASE_URI` and, for sqlite files,
add missing columns using `ALTER TABLE`.
"""
import sqlite3
import os
from urllib.parse import urlparse
from app import app


def run_migrations():
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not uri:
            print('No database URI configured')
            return

        if uri.startswith('sqlite:///'):
            db_path = uri.replace('sqlite:///', '')
        elif uri.startswith('sqlite:'):
            # fallback
            db_path = uri.split(':', 1)[1]
        else:
            print('Only sqlite databases are supported by this helper.')
            return

        # If the path is not absolute, try common locations (app.instance_path)
        if not os.path.isabs(db_path) and not os.path.exists(db_path):
            alt = os.path.join(app.instance_path, os.path.basename(db_path))
            if os.path.exists(alt):
                db_path = alt
            else:
                print(f'Database file not found: {db_path}')
                return

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("PRAGMA table_info('users')")
        cols = [r[1] for r in cur.fetchall()]

        if 'password_hash' not in cols:
            print('Adding column: password_hash')
            cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        else:
            print('Column password_hash already present')

        if 'is_admin' not in cols:
            print('Adding column: is_admin')
            cur.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        else:
            print('Column is_admin already present')

        conn.commit()
        conn.close()
        print('Migration complete')


if __name__ == '__main__':
    run_migrations()
