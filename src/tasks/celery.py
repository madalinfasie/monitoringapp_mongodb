from celery import Celery

import settings
import main
from tasks import periodic_tasks


app = Celery(main.app.name, broker=settings.CELERY_BROKER_URL)
app.conf.update(main.app.config)
app.conf.beat_schedule = periodic_tasks.SCHEDULES
app.conf.imports = settings.CELERY_IMPORTS
