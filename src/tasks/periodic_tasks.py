from datetime import timedelta


SCHEDULES = {
    'collect_published_articles': {
        'task': 'tasks.tasks.collect',
        'kwargs': {'collector': 'collect_published_articles'},
        'schedule': timedelta(seconds=15)
    }
}