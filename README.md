# Metric Monitoring App Using Mongo Time Series

## Description

Schedule metrics collectors for different services and run anomaly detection on new values.

This app has been developed for the MongoDB Hackathon on Dev.to and won the [runner-up prize](https://dev.to/devteam/congrats-to-the-mongodb-atlas-hackathon-winners-4cc0).

## Getting started

### Prerequisites

Make sure you have Docker and Docker Compose installed on your machine.

Create a MongoDB Atlas cluster with MongoDB 5.0 or above installed.

For security reasons, the `.env` was not included in the repository. The available configuration variables are provided inside `.env.sample`. Make sure to set all the configuration variables before running the app.

### Running the app

Running this app is as easy as running:

```
$ docker-compose build
$ docker-compose up
```

## Overview

Starting with the `docker-compose.yml` file, we can see that this application is split into a main webapp service and the scheduling service (`celery` in this case).

The metrics collection is done mainly by the `celery` workers. The `metrics_web` service providing only a way of pushing metrics from external service (when scheduling is not feasible).

### Metric collection

All metric collectors should be placed in `metrics.py` file. A collector is a simple function that connects to an external service (usually through REST API or Database connection), aggregates the values and sends the metric value to the MongoDB storage system.

The collectors are scheduled and run by the `celery beat`.

### Anomaly detection

#### Training

To enable anomaly detection on a given metric, first you have to add it into `resources/detection_metrics.json` file. The training process will look inside this file and collect data from all the metrics given in the json.

The json file can have the following fields:

`name`: _required_, the name of the metric

`train_params`: _optional_, a dictionary that will be passed as parameters to the training model

`train_interval`: _optional_, a dictionary that will be passed as parameters to a timedelta object. This interval is used for data selection before running the training process.

The `components.anomaly_detector.Detector` class acts as a Facade for the actual model inside `components.anomaly_models` module. The detector can only use a single prediction model and it has the role of collecting the metrics from the `detetection_metrics.json` file and running the training and prediction processes for every metric it finds.

The training process is scheduled and run by the `celery beat` the same as the collectors.

The models will be saved on disk named after the template: `{metric_name}_{model_name}_{metric_labels}.joblib`. For prediction, the same pattern will be used to search for available models, so in order for a prediction to be made, you have to be sure a model exists for that particular model-metric-labels configuration.

You can also run manual training through an API endpoint from `metrics_web` service:

_URL:_ `/push`

_Method:_ `POST`

_Example:_ `GET localhost:5000/anomaly-detection/train`


#### Prediction

To get a prediction, one can use `components.anomaly_detector.Detector.predict` method which receives a metric name and a metric_info dictionary and returns `-1` for outliers and `1` for inliers.

A metric_info object is a dictionary that contains the fields: `labels`, `value` and `timestamp`.

The collector will be tasked with storing the prediction result inside the metric before sending it to the storage.

### Push metrics manually

Scheduling collectors is the main way of gathering metrics data, but when this is not possible, a manual push mechanism is available in the `metrics_web` service.

The push mechanism has only one endpoint:

_URL:_ `/push`

_Method:_ `POST`

_Body:_

- `name`: _required_, metric name
- `value`: _required_, the metric value
- `labels`: _optional_, a labels dictionary to better describe the entry

The new entry will be added with timestamp `datetime.now()`.

#### Example:

`POST localhost:5000/push`

Body:
```
{
    "name": "metric_name",
    "labels": {"label1": "value1"}
    "value": 123
}
```

## Visualization

To visualize the metrics data, tools such as Mongo Charts or Grafana can be used.

To do that, create a data source using the tool of your choice pointing to the MongoDb database that holds all the metrics and then create the graphs.

_Note:_ Currently, Grafana supports MongoDb only with paid subscription.
