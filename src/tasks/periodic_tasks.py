from datetime import timedelta


SCHEDULES = {
    'run_anomaly_detection_training': {
        'task': 'tasks.tasks.run_training',
        'schedule': timedelta(days=1)
    },
    # Metric collectors
    'collect_a_random_metric': {
        'task': 'tasks.tasks.collect',
        'kwargs': {'collector': 'collect_a_random_metric'},
        'schedule': timedelta(seconds=15)
    },
    'collect_a_random_metric_with_prediction': {
        'task': 'tasks.tasks.collect',
        'kwargs': {'collector': 'collect_a_random_metric_with_prediction'},
        'schedule': timedelta(seconds=30)
    },
    'collect_fresh_published_articles_devto': {
        'task': 'tasks.tasks.collect',
        'kwargs': {'collector': 'collect_fresh_published_articles_devto'},
        'schedule': timedelta(hours=1)
    }
}