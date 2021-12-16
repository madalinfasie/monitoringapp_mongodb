import metrics
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