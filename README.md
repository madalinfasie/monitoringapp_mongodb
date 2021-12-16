# Metric Monitoring App Using Mongo Time Series

This app will
    - Have a scheduler that stores new metric values in mongodb
    - Pass those values to an anomaly detection process
    - Train models only for a selected number of metrics
    - Run scheduled predictions for the selected metrics
    - Graph the data in grafana

