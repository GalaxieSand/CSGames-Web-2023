
def bad_request(message="Bad Request"):
    return message, 400


def not_found(message="Not Found"):
    return message, 404


def not_authorized(message="UNAUTHORIZED"):
    return message, 401


def forbidden(message="FORBIDDEN"):
    return message, 403


def no_content():
    return "", 204