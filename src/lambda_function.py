import json
from flask import Flask, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wrappers import Request, Response

app = Flask(__name__)

# Apply ProxyFix to handle headers correctly in AWS Lambda
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/api/send-document', methods=['GET'])
def send_document():
    # Simulate an event and context
    event = {
        'httpMethod': 'GET',
        'path': '/send-document',
        'queryStringParameters': request.args,
        'headers': dict(request.headers),
        'body': None
    }
    context = {}

    # Call the handler function
    response = handler(event, context)

    # Return the response from the handler
    return jsonify(response)


def handler(event, context):
    print(event, context)
    data = {"last_name": "rojas", "name": "nelson"}
    return data


if __name__ == "__main__":
    app.run(debug=True)
