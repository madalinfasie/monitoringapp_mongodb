import metrics
from celery import app


@app.task
def collect(collector: str, *args, **kwargs) -> None:
    """ Run a given `collector` from metrics module.

    If args or kwargs are passed, they will be passed to the collector function as parameters
    """
    if not hasattr(metrics, collector):
        print('No collector found: {}'.format(collector))
        return

    getattr(metrics, collector)(*args, **kwargs)