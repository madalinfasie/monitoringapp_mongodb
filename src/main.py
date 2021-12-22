import flask

from components import storage


app = flask.Flask(__name__)


@app.route('/test')
def test():
    from tasks import tasks
    tasks.run_training()
    return 'Success'


@app.route('/push', methods=['POST'])
def push_metric():
    """ Push a metric from an external service to Mongo

    Request body:
    {
        "name": "metric_name",
        "labels": {"label1": "value1"}
        "value": 123
    }

    Fields name and value are mandatory, labels is not.
    """
    request_body = flask.request.get_json(force=True)

    if not request_body.get('value'):
        return flask.Response('Invalid request, value is mandatory', status=400)

    if not request_body.get('name'):
        return flask.Response('Invalid request, name is mandatory', status=400)

    metric_storage = storage.MongoStorage()
    metric_storage.store_metric(
        collection=request_body['name'],
        value=request_body['value'],
        labels=request_body.get('labels'))

    return flask.Response(status=204)


if __name__ == '__main__':
    app.run()