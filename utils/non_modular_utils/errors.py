StandardError = "standard_error"
GenericError = "generic_error"


class ErrorException(Exception):

    def __init__(self, message=None, error_type=None, meta=None, code=None):
        self.context = {}
        if code is not None:
            self.context["code"] = code
        self.context["error_type"] = error_type
        self.context["meta"] = meta

        super().__init__(message)
