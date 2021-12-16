from celery import Celery

import periodic_tasks
import settings
import main


app = Celery(main.app.name, broker=settings.CELERY_BROKER_URL)
app.conf.update(main.app.config)
app.conf.beat_schedule = periodic_tasks.SCHEDULES

# Add this if celery is going to be used with routes
# class ContextTask(app.Task):
#     def __call__(self, *args, **kwargs):
#         with app.app_context():
#             return self.run(*args, **kwargs)

# app.Task = ContextTask
