import abc
import pathlib

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

import settings
from data_classes import Metric


class ModelDoesNotExistError(Exception):
    pass


class Model(abc.ABC):
    model_name: str = ''

    def train(self, df: pd.DataFrame) -> None:
        pass

    def predict(self, df: pd.DataFrame) -> int:
        pass


class IForestModel(Model):
    model_name = 'sklearn_iforest'

    def __init__(self, metric: Metric) -> None:
        self.metric = metric
        self._model_path = None

    @property
    def model_path(self):
        if not self._model_path:
            self._model_path = self._build_model_path()

        return self._model_path

    def train(self, df: pd.DataFrame) -> None:
        """ Train a given dataset """
        df = df[['timestamp', 'value']]
        df = self._split_timestamp_in_features(df)
        model = IsolationForest(warm_start=True, **self.metric.train_params)
        model.fit(df)

        self._save_model(model)

    def predict(self, df: pd.DataFrame) -> int:
        """ Predict the df """
        df = df[['timestamp', 'value']]
        df = self._split_timestamp_in_features(df)
        model = self._load_model()
        return int(model.predict(df)[0])

    def _build_model_path(self) -> str:
        """ Build the path and the name of the model file """
        return '{metric_name}_{model_name}{labels}.joblib'.format(
            metric_name=self.metric.name,
            model_name=self.model_name,
            labels='_' + '_'.join(self.metric.labels.values()) if self.metric.labels else ''
        )

    def _split_timestamp_in_features(self,
            df: pd.DataFrame,
            column: str = 'timestamp') -> pd.DataFrame:
        """ Split the time column from dataframe into separate features """
        df = df.copy()
        df[column] = pd.to_datetime(df[column])
        df.set_index(column, drop=True, inplace=True)
        df['day'] = [i.day for i in df.index]
        df['day_of_year'] = [i.dayofyear for i in df.index]
        df['week_of_year'] = [i.weekofyear for i in df.index]
        df['hour'] = [i.hour for i in df.index]
        df['is_weekday'] = [i.isoweekday() for i in df.index]
        return df

    def _save_model(self, model: IsolationForest) -> None:
        """ Save the given model into a file """
        models_path = pathlib.Path(settings.MODELS_PATH)
        if not models_path.exists():
            models_path.mkdir(parents=True)

        joblib.dump(model, str(models_path / self._build_model_path()))

    def _load_model(self) -> IsolationForest:
        """ Load a previously saved model based on the metric attributes """
        models_path = pathlib.Path(settings.MODELS_PATH)
        try:
            return joblib.load(str(models_path / self._build_model_path()))
        except FileNotFoundError as e:
            raise ModelDoesNotExistError(e)