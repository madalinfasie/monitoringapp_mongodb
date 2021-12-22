import json
import typing as t
from datetime import datetime, timedelta

import pandas as pd

import settings
import custom_types as types
from components import storage, anomaly_models as ad_models
from data_classes import Metric


class Detector:
    def __init__(self, predictor_model: ad_models.Model = ad_models.IForestModel):
        self.predictor_model = predictor_model
        self.metrics_path = settings.DETECTION_METRICS_PATH
        self.storage = storage.MongoStorage()

        self._metrics = None

    @property
    def metrics(self) -> t.List[Metric]:
        if not self._metrics:
            self._metrics = self._parse(self.metrics_path)

        return self._metrics

    def train(self) -> None:
        """ Run the training process for all the metrics in the detection metrics file """
        for metric in self.metrics:
            print(f'[TRAIN] Training metric {metric}')
            distinct_labels = self.storage.get_distinct_in_range(
                collection=metric.name,
                start=datetime.now() - timedelta(**metric.train_interval))

            print(f'[TRAIN] Distinct labels for the metric {metric}: {distinct_labels}')
            if not distinct_labels:
                self._train_metric(metric)
                continue

            for labels in distinct_labels:
                metric.labels = labels
                self._train_metric(metric)

    def predict(self, metric_name: str, metric_obj: types.MongoDocument) -> int:
        """ Run predictions for all the metrics in the detection metrics file.

        Returns: -1 for outliers and 1 for inliers
        """
        metric = Metric(name=metric_name, labels=metric_obj.get('labels'))
        model = self.predictor_model(metric)

        return model.predict(pd.DataFrame(data=[metric_obj]))

    def _parse(self, path: str) -> t.List[Metric]:
        """ Parse a json file from `path` and create a list of Metric objects """
        with open(path) as f:
            json_metrics = json.load(f)

        return [Metric(**data) for data in json_metrics]

    def _train_metric(self, metric: Metric) -> None:
        """ Run the training process for a given metric """
        model = self.predictor_model(metric)

        data = self.storage.get_metric_data(
            collection=metric.name,
            labels=metric.labels,
            start=datetime.now() - timedelta(**metric.train_interval))

        data = tuple(data)
        if not data:
            print('WARNING! No data found for metric', metric)
            return

        model.train(pd.DataFrame(data=data))