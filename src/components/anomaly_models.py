import abc
import pathlib
from datetime import datetime

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

import settings
from components.data_classes import Metric


class Model(abc.ABC):
    model_name: str = ''

    def train(self, data: pd.DataFrame) -> None:
        pass

    def predict(self, timestamp: datetime) -> pd.DataFrame:
        pass


class IForestModel(Model):
    model_name = 'sklearn_iforest'

    def __init__(self, metric: Metric) -> None:
        self.metric = metric
        self._model_path = None
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)

    @property
    def model_path(self):
        if not self._model_path:
            self._model_path = self._build_model_path()

        return self._model_path

    def train(self, data: pd.DataFrame) -> None:
        """ Train a given dataset """
        data = data[['timestamp', 'value']]
        data = self._split_timestamp_in_features(data)
        model = IsolationForest(n_estimators=10, warm_start=True)
        model.fit(data)

        self._save_model(model)

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """ Predict the data """
        data = self._split_timestamp_in_features(data)
        model = self._load_model()
        forecast = model.predict(data)
        return forecast

    def _build_model_path(self):
        """ Build the path and the name of the model file """
        return '{metric_name}_{model_name}{labels}.joblib'.format(
            metric_name=self.metric.name,
            model_name=self.model_name,
            labels='_' + '_'.join(self.metric.labels.values()) if self.metric.labels else ''
        )

    def _split_timestamp_in_features(self,
            data: pd.DataFrame,
            column: str = 'timestamp') -> None:
        """ Split the time column from dataframe into separate features """
        data = data.copy()
        data[column] = pd.to_datetime(data[column])
        data.set_index(column, drop=True, inplace=True)
        data['day'] = [i.day for i in data.index]
        data['day_of_year'] = [i.dayofyear for i in data.index]
        data['week_of_year'] = [i.weekofyear for i in data.index]
        data['hour'] = [i.hour for i in data.index]
        data['is_weekday'] = [i.isoweekday() for i in data.index]
        return data

    def _save_model(self, model) -> None:
        """ Save the given model into a file """
        models_path = pathlib.Path(settings.MODELS_PATH)
        if not models_path.exists():
            models_path.mkdir(parents=True)

        joblib.dump(model, str(models_path / self._build_model_path()))

    def _load_model(self):
        """ Load a previously saved model based on the metric attributes """
        models_path = pathlib.Path(settings.MODELS_PATH)
        return joblib.load(str(models_path / self._build_model_path()))