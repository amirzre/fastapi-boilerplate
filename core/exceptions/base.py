from http import HTTPStatus


class CustomException(Exception):
    """
    A custom exception class for general HTTP errors.

    This class is used as a base for specific exceptions with predefined HTTP status codes.
    It allows for a customizable error message while using default HTTP status codes and error codes.

    Attributes:
        code (HTTPStatus): The HTTP status code associated with the exception.
        error_code (HTTPStatus): The error code associated with the exception, often the same as the HTTP status code.
        message (str): A message describing the error, defaulting to the description of the associated HTTP status.
    """

    code = HTTPStatus.BAD_GATEWAY
    error_code = HTTPStatus.BAD_GATEWAY
    message = HTTPStatus.BAD_GATEWAY.description

    def __init__(self, message=None):
        """
        Initializes the exception with an optional custom message.

        Args:
            message (str, optional): A custom message for the exception. Defaults to None.
        """
        if message:
            self.message = message


class InternalException(CustomException):
    """
    Exception raised for HTTP 500 Internal Server Error.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Internal Server Error (500).
        error_code (HTTPStatus): The error code for Internal Server Error (500).
        message (str): The message for Internal Server Error, defaulting to the description of HTTP 500.
    """

    code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = HTTPStatus.INTERNAL_SERVER_ERROR
    message = HTTPStatus.INTERNAL_SERVER_ERROR.description


class BadRequestException(CustomException):
    """
    Exception raised for HTTP 400 Bad Request.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Bad Request (400).
        error_code (HTTPStatus): The error code for Bad Request (400).
        message (str): The message for Bad Request, defaulting to the description of HTTP 400.
    """

    code = HTTPStatus.BAD_REQUEST
    error_code = HTTPStatus.BAD_REQUEST
    message = HTTPStatus.BAD_REQUEST.description


class NotFoundException(CustomException):
    """
    Exception raised for HTTP 404 Not Found.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Not Found (404).
        error_code (HTTPStatus): The error code for Not Found (404).
        message (str): The message for Not Found, defaulting to the description of HTTP 404.
    """

    code = HTTPStatus.NOT_FOUND
    error_code = HTTPStatus.NOT_FOUND
    message = HTTPStatus.NOT_FOUND.description


class ForbiddenException(CustomException):
    """
    Exception raised for HTTP 403 Forbidden.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Forbidden (403).
        error_code (HTTPStatus): The error code for Forbidden (403).
        message (str): The message for Forbidden, defaulting to the description of HTTP 403.
    """

    code = HTTPStatus.FORBIDDEN
    error_code = HTTPStatus.FORBIDDEN
    message = HTTPStatus.FORBIDDEN.description


class UnauthorizedException(CustomException):
    """
    Exception raised for HTTP 401 Unauthorized.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Unauthorized (401).
        error_code (HTTPStatus): The error code for Unauthorized (401).
        message (str): The message for Unauthorized, defaulting to the description of HTTP 401.
    """

    code = HTTPStatus.UNAUTHORIZED
    error_code = HTTPStatus.UNAUTHORIZED
    message = HTTPStatus.UNAUTHORIZED.description


class UnprocessableEntity(CustomException):
    """
    Exception raised for HTTP 422 Unprocessable Entity.

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Unprocessable Entity (422).
        error_code (HTTPStatus): The error code for Unprocessable Entity (422).
        message (str): The message for Unprocessable Entity, defaulting to the description of HTTP 422.
    """

    code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = HTTPStatus.UNPROCESSABLE_ENTITY
    message = HTTPStatus.UNPROCESSABLE_ENTITY.description


class DuplicateValueException(CustomException):
    """
    Exception raised for HTTP 422 Unprocessable Entity due to duplicate values.

    This exception is used when the operation cannot be completed due to a duplicate value
    (e.g., a unique constraint violation).

    Inherits from CustomException with a predefined HTTP status code and message.

    Attributes:
        code (HTTPStatus): The HTTP status code for Unprocessable Entity (422).
        error_code (HTTPStatus): The error code for Unprocessable Entity (422).
        message (str): The message for duplicate value error, defaulting to the description of HTTP 422.
    """

    code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = HTTPStatus.UNPROCESSABLE_ENTITY
    message = HTTPStatus.UNPROCESSABLE_ENTITY.description
