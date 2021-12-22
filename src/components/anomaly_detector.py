import json
import typing as t
from datetime import datetime, timedelta

import pandas as pd

import settings
from components import storage, anomaly_models as ad_models
from components.data_classes import Metric


class Detector:
    def __init__(self,
            predictor_model: ad_models.Model,
            storage: storage.BaseStorage):
        self.predictor_model = predictor_model
        self.metrics_path = settings.DETECTION_METRICS_PATH
        self.storage = storage

        self._metrics = None

    @property
    def metrics(self) -> t.List[Metric]:
        if not self._metrics:
            self._metrics = self._parse(self.metrics_path)

        return self._metrics

    def train(self) -> None:
        """ Run the training process for all the metrics in the detection metrics file """
        for metric in self.metrics:
            distinct_labels = self.storage.get_distinct_in_range(
                collection=metric.name,
                start=datetime.now() - timedelta(**metric.train_interval))

            for labels in distinct_labels:
                metric.labels = labels
                model = self.predictor_model(metric)

                data = self.storage.get_metric_data_by_labels(
                    collection=metric.name,
                    labels=metric.labels,
                    start=datetime.now() - timedelta(**metric.train_interval))

                data = tuple(data)
                if not data:
                    print('WARNING! No data found for metric', metric)
                    continue

                model.train(pd.DataFrame(data=data))

    def predict(self, data: t.Dict[str, t.Any]) -> None:
        """ Run predictions for all the metrics in the detection metrics file.

        This method will add the detected values to the storage system
        """
        metric = Metric(name=data['name'], labels=data['labels'])
        model = self.predictor_model(metric)

        data = {
            'timestamp': [data['timestamp']],
            'value': [data['value']]
        }
        return model.predict(pd.DataFrame(data=data))[0]

    def _parse(self, path: str) -> t.List[Metric]:
        """ Parse a json file from `path` and create a list of Metric objects """
        with open(path) as f:
            json_metrics = json.load(f)

        return [Metric(**data) for data in json_metrics]
