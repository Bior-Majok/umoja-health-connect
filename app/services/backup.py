"""NFR13: automated database backups every 24 hours.

For the SQLite dev/demo database this copies the file to instance/backups/. When a real
Postgres DATABASE_URL is configured (see config.py), backups are the hosting provider's
job (e.g. Render's managed Postgres takes its own automated snapshots) — this function
just logs that fact rather than trying to reinvent pg_dump scheduling.
"""

import os
import shutil
from datetime import datetime

from flask import current_app


def run_backup():
    uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not uri.startswith('sqlite:///'):
        current_app.logger.info('[BACKUP] Skipped — managed database backups are handled by the hosting provider.')
        return None

    relative_path = uri.replace('sqlite:///', '', 1)
    db_path = relative_path if os.path.isabs(relative_path) else os.path.join(current_app.instance_path, relative_path)
    if not os.path.exists(db_path):
        current_app.logger.warning('[BACKUP] Database file not found at %s', db_path)
        return None

    backups_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backups_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    dest = os.path.join(backups_dir, f'umoja_health_{timestamp}.db')
    shutil.copy2(db_path, dest)
    current_app.logger.info('[BACKUP] Database backed up to %s', dest)
    return dest
