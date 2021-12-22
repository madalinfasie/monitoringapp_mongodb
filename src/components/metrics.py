import random
import typing as t

from components import storage


def collect_published_articles():
    value = random.randrange(1, 100)
    metric_storage = storage.MongoStorage()
    metric_storage.store_metric('published_articles', value, labels={'user': 'ion'})
