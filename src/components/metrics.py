import random
import typing as t
from datetime import datetime, timedelta

import requests

from components import storage, anomaly_detector as ad, anomaly_models as ad_models


def _apply_prediction(
        name: str,
        value: t.Union[float, int],
        labels: t.Optional[t.Dict[str, str]] = None,
        timestamp: t.Optional[datetime]=None) -> t.Dict[str, t.Any]:
    """ Run prediction and update the metric dictionary with the prediction result

    name: metric name
    value: metric value
    labels: metric labels. Default: No initial labels will be set.
    timestamp: the date at which the point will be inserted. Default: datetime.now()

    Returns a dictionary of metric information including a new "anomaly" field
    """
    detector = ad.Detector()
    timestamp = timestamp or datetime.now()
    metric_info = {
        'collection': name,
        'timestamp': timestamp,
        'value': value,
        'labels': labels or {}
    }

    try:
        metric_info.setdefault('labels', {})['anomaly'] = detector.predict(
            metric_name=name,
            metric_info=metric_info)
    except ad_models.ModelDoesNotExistError:
        print(f'No model trained yet for metric {name}! Skipping predictions.')

    return metric_info


def collect_a_random_metric() -> None:
    """ A dummy collection metric that adds random numbers to collection """
    value1 = random.randrange(1, 100)
    value2 = random.randrange(1, 100)
    metric_storage = storage.MongoStorage()
    metric_storage.store_metric(collection='random_metric', value=value1, labels={'user': 'ion'})
    metric_storage.store_metric(collection='random_metric', value=value2, labels={'user': 'maria'})


def collect_a_random_metric_with_prediction() -> None:
    """ A dummy collection metric that adds random numbers to collection """
    value1 = random.randrange(1, 100)
    value2 = random.randrange(1, 100)
    metric_storage = storage.MongoStorage()

    metric_info1 = _apply_prediction(
        name='random_metric_with_prediction',
        value=value1,
        labels={'user': 'ion'})

    metric_info2 = _apply_prediction(
        name='random_metric_with_prediction',
        value=value2,
        labels={'user': 'maria'})

    metric_storage.store_metric(**metric_info1)
    metric_storage.store_metric(**metric_info2)


def collect_fresh_published_articles_devto() -> None:
    """ Collect count of articles published on Dev.to in the last hour """
    metric_storage = storage.MongoStorage()

    # Count the fresh articles from API
    url = 'https://dev.to/api/articles?page=1&per_page=1000&state=fresh'
    result = requests.get(url)
    result.raise_for_status()

    articles_last_hour = len([0 for obj in result.json()
        if obj['published_at'] > (datetime.now() - timedelta(hours=1)).isoformat()])

    # Run predictions and store the metric value
    metric_info = _apply_prediction(
        name='published_articles_last_hour',
        value=articles_last_hour)

    metric_storage.store_metric(**metric_info)
