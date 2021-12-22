import abc
import typing as t
from datetime import datetime

import pymongo
from bson.code import Code

import settings


class BaseStorage(abc.ABC):
    @staticmethod
    @abc.abstractstaticmethod
    def store_metric(collection: str, value: float, labels: t.Dict[str, str]) -> None:
        pass


class MongoStorage(BaseStorage):
    def __init__(self):
        self.client = pymongo.MongoClient(settings.MONGO_URL)
        self.db = self.client[settings.MONGO_DB_NAME]

    def store_metric(self,
            collection: str,
            value: float,
            labels: t.Dict[str, str],
            timestamp: t.Optional[datetime] = None) -> None:
        """ Store a new metrics instance into MongoDB storage system """
        timestamp = timestamp or datetime.now()
        if collection not in self.db.list_collection_names():
            self.db.create_collection(
                collection,
                timeseries={'timeField': 'timestamp', 'metaField': 'labels'})

        self.db[collection].insert_one({
            'timestamp': timestamp.isoformat(),
            'labels': labels,
            'value': value
        })

    def get_distinct_in_range(self, collection: str, start: datetime) -> t.Dict[str, t.Any]:
        """ Select distinct labels starting from a given timestamp """
        return self.db[collection].distinct('labels', {'timestamp': {'$gte': start.isoformat()}})

    def get_metric_data_by_labels(self,
            collection: str,
            labels: t.Dict[str, str],
            start: datetime) -> t.Dict[str, t.Any]:
        """ Select documents starting from an optional `start` date filtered by `labels` """
        find_params = {'labels': labels, 'timestamp': {'$gte': start.isoformat()}}

        print('findparams', find_params)

        return self.db[collection].find(find_params).sort([('timestamp', -1)])
