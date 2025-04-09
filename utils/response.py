from flask import jsonify


def success_response(msg, data=None):
    """
    Returns a success response with message, data, and status code 200.
    """
    if not data:
        data = []
    return jsonify({'message': msg, 'data': data, 'status': 200}), 200


def not_found_error(msg):
    """
    Returns a not found error response with message and status code 404.
    """
    return jsonify({'message': msg, 'status': 404}), 404


def bad_request_error(msg, data=None):
    """
    Returns a bad request error response with message and status code 400.
    """
    if not data:
        data = []
    return jsonify({'message': msg, 'data': data, 'status': 400}), 400


def server_error(msg):
    """
    Returns a server error response with message and status code 500.
    """
    return jsonify({'message': msg, 'status': 500}), 500

def list_response(rows):
    response = {
        'data': {
            'rows': rows
        }
    }

    return jsonify(response)


def detail_response(data):
    response = {
        'data': data
    }
    return jsonify(response)


def validation_error(msg):
    """
    Raises a validation error with the provided message and optional field name.
    """
    if isinstance(msg, str):
        return jsonify({'message': msg, 'status': 400})
    else:
        errors = msg.messages
        for field, messages in errors.items():
            return jsonify({'error': 'Validation Error', 'message': messages[0], 'field': field, 'status': 400}), 400

