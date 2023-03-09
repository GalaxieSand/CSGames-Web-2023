
class HTTP:
    class Methods:
        (POST, GET) = ('POST', 'GET')

    class StatusCode:
        (OK, Created, NoContent) = (200, 201, 204)
        (BadRequest, Unauthorized, Forbidden, NotFound) = (400, 401, 403, 404)

    class MimeType:
        (PlainText, ApplicationJSON, UrlFormEncoded) = ("text/plain", "application/json", "application/x-www-form-urlencoded")

    class Consumes:
        (UrlEncodedForm) = ("x-url-encoded-form")