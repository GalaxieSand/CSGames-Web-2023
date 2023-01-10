import json


class ResponseValidator:
    def __init__(self, name):
        self.name = name

    def is_valid(self, response):
        raise NotImplementedError()

    def get_failure_message(self, response):
        raise NotImplementedError()


class ResponseStatusCodeValidator(ResponseValidator):
    def __init__(self, status_code=200):
        ResponseValidator.__init__(self, "Response Status Code Validator")
        self.status_code = status_code

    def is_valid(self, response):
        return response.getcode() == self.status_code

    def get_failure_message(self, response):
        return "Status Code Expected was {0}, received {1} instead".format(self.status_code, response.getcode())


class JsonContentResponseValidator(ResponseValidator):
    def __init__(self, lambda_validator):
        ResponseValidator.__init__(self, "Json Content Response Validator")
        self.lambda_validator = lambda_validator
        self.failure_details = ""

    def is_valid(self, response):
        json_data = json.load(response)

        test_result, failure_message = self.lambda_validator(json_data)

        if failure_message is not None:
            self.failure_details = failure_message

        return test_result

    def get_failure_message(self, response):
        return "Json Content Validator has failed, Details: {0}".format(self.failure_details)

class HttpErrorValidator:
    def __init__(self, name):
        self.name = name

    def is_valid(self, http_error):
        raise NotImplementedError()

    def get_failure_message(self, response):
        raise NotImplementedError()

class HttpErrorStatusCodeValidator(HttpErrorValidator):
    def __init__(self, status_code):
        HttpErrorValidator.__init__(self, "Http Error Status Code Validator")
        self.status_code = status_code

    def is_valid(self, http_error):
        return http_error.getcode() == self.status_code

    def get_failure_message(self, response):
        return "Http Error Status Code Expected was {0}, received {1} instead".format(self.status_code, response.getcode())