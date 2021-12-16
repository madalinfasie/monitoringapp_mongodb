import flask

import storage


app = flask.Flask(__name__)


@app.route('/push/<metric_name>')
def push_metric(metric_name):
    request_body = flask.request.json(force=True)

    if not request_body.get('value'):
        return flask.Response('Invalid request, value is mandatory', status=400)

    metric_storage = storage.MongoStorage()
    metric_storage.store_metric(
        name=metric_name,
        value=request_body['value'],
        labels=request_body.get('labels'))

    return flask.Response(status=204)


if __name__ == '__main__':
    app.run()