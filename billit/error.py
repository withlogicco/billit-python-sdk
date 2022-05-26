class Error:
    """
    Base class for all API errors
    """

    def __init__(self, message, response_status_code=None):
        self.message = message
        self.response_status_code = response_status_code

    def __str__(self):
        return self.message

    def handle_error(self):
        if self.response_status_code >= 401:
            pass
