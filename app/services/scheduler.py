"""Background scheduler wiring for the two periodic jobs required by the SRS:
NFR15 (consultation SLA auto-escalation) and NFR13 (24h database backups).
"""

import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

_scheduler = None


def start_scheduler(app):
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    # Flask's debug reloader spawns a second process; only the reloader's child process
    # (WERKZEUG_RUN_MAIN=true) should actually run the scheduler, or jobs fire twice.
    if app.debug and os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return None

    from app.routes.consultations import run_escalation_sweep
    from app.services.backup import run_backup

    def _escalation_job():
        with app.app_context():
            run_escalation_sweep()

    def _backup_job():
        with app.app_context():
            run_backup()

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_escalation_job, 'interval', minutes=5, id='escalation-sweep', replace_existing=True)
    scheduler.add_job(
        _backup_job, 'interval', hours=24, id='daily-backup', replace_existing=True, next_run_time=datetime.now()
    )
    scheduler.start()
    _scheduler = scheduler
    return scheduler
