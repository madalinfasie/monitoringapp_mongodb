import time

from components import anomaly_detector as ad, anomaly_models as ad_models, metrics
from tasks.celery import app


@app.task
def collect(collector: str, args=None, kwargs=None) -> None:
    """ Run a given `collector` from metrics module.

    If args or kwargs are passed, they will be passed to the collector function as parameters
    """
    if not hasattr(metrics, collector):
        print('No collector found: {}'.format(collector))
        return

    args, kwargs = args or tuple(), kwargs or dict()

    print(f'Starting collecting metric {collector}')
    getattr(metrics, collector)(*args, **kwargs)
    print(f'Finished collecting metric {collector}')


@app.task
def run_training() -> None:
    """ Run the anomaly detection training """
    detector = ad.Detector(ad_models.IForestModel)
    print('Starting metrics training')
    start = time.time()
    detector.train()
    print(f'Finished training metrics in {time.time() - start:.2f}s')
