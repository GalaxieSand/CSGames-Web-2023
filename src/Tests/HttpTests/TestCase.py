import urllib


class TestCase:
    (ExceptionThrown, ValidatorFailure) = (1, 2)

    def __init__(self, name, url, method="GET", response_validators=[], http_error_validators=[], headers={}, request_body=None, completed_callback=None):
        self.name = name
        self.method = method
        self.url = url
        self.response_validators = response_validators
        self.http_error_validators = http_error_validators
        self.headers = headers
        self.request_body = request_body
        self.completed_callback = completed_callback

        # inner states variables
        self.messages = []
        self.exception = None
        self.success = False
        self.failed_reason = None

    def run(self):
        test_success = True

        request = urllib.request.Request(self.url, method=self.method, headers=self.headers, data=self.request_body)

        try:
            resp = urllib.request.urlopen(request)

            if len(self.http_error_validators) > 0:
                # we got a failed test
                self.success = False
                self.failed_reason = self.ValidatorFailure
                return

            for validator in self.response_validators:
                if not validator.is_valid(resp):
                    self.messages.append("\tValidator {0} has returns false".format(validator.name))
                    self.messages.append("\t\t{0}".format(validator.get_failure_message(resp)))
                    test_success = False
                    self.failed_reason = self.ValidatorFailure
                    break

        except Exception as err:
            if len(self.response_validators) > 0:
                # we got a failed
                self.exception = err
                self.failed_reason = self.ExceptionThrown
                self.messages.append("\tAn exception has been thrown")
                self.messages.append("\t\t{0}".format(str(err)))
                self.success = False
                return

            for validator in self.http_error_validators:
                if not validator.is_valid(err):
                    self.messages.append("\tValidator {0} has returns false".format(validator.name))
                    self.messages.append("\t\t{0}".format(validator.get_failure_message(err)))
                    test_success = False
                    self.failed_reason = self.ValidatorFailure
                    break

        self.success = test_success

        if self.completed_callback is not None:
            self.completed_callback(self)
