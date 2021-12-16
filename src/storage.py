import abc
import typing as t
from datetime import datetime

import pymongo

import settings


class BaseStorage(abc.ABC):
    @staticmethod
    @abc.abstractstaticmethod
    def store_metric(name: str, value: float, labels: t.Dict[str, str]) -> None:
        pass


class MongoStorage(BaseStorage):
    @staticmethod
    def store_metric(
            name: str,
            value: float,
            labels: t.Dict[str, str],
            timestamp: t.Optional[datetime] = None) -> None:
        """ Store a new metrics instance into MongoDB storage system """
        timestamp = timestamp or datetime.now()
        with pymongo.MongoClient(settings.MONGO_URL) as client:
            db = client[settings.MONGO_DB_NAME]
            db.create_collection(name, timeseries={'timeField': 'timestamp', 'metaField': 'labels'})
            db[name].insert_one({
                'timestamp': timestamp.isoformat(),
                'labels': labels,
                'value': value
            })
