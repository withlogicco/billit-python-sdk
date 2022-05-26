class Error(Exception):
    """
    Base class for all API errors
    """

    def __init__(self, message, response_status_code=None):
        self.message = message
        self.response_status_code = response_status_code

    def __str__(self):
        return f"Error code {self.response_status_code}, Error message: {self.message}"


class AuthenticationError(Error):
    pass


class ApiError(Error):
    pass


class InvalidEnvironment(Exception):
    def __init__(self, environment):
        self.environment = environment

    def __str__(self) -> str:
        return f"Invalid environment provided: {self.environment}"
