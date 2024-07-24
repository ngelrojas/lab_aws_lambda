from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.wrappers import Request, Response


app = Flask(__name__)

# Apply ProxyFix to handle headers correctly in AWS Lambda
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route('/send-document')
def send_document():
    return jsonify(message="Hello, World!")


def handler(event, context):
    # Convert the API Gateway event to a WSGI request
    request = Request.from_values(
        method=event['httpMethod'],
        path=event['path'],
        query_string=event['queryStringParameters'],
        headers=event['headers'],
        data=event['body']
    )

    # Create a response object
    response = Response()

    # Dispatch the request to the Flask app
    app.wsgi_app(request.environ, response.start_response)

    # Return the response as a dictionary
    return {
        'statusCode': response.status_code,
        'headers': dict(response.headers),
        'body': response.get_data(as_text=True)
    }


if __name__ == "__main__":
    app.run(debug=True)
