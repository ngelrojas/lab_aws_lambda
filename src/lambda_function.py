# import json

from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

# from werkzeug.wrappers import Request, Response

app = Flask(__name__)

app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route("/api/send-document", methods=["GET"])
def send_document():
    event = {
        "httpMethod": "GET",
        "path": "/send-document",
        "queryStringParameters": request.args,
        "headers": dict(request.headers),
        "body": None,
    }
    context = {}

    response = handler(event, context)

    return jsonify(response)


def handler(event, context):
    print(event, context)
    data = {"last_name": "rojas", "name": "nelson"}
    return data


if __name__ == "__main__":
    app.run(debug=True)
