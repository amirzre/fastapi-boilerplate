import re
from typing import Annotated

from pydantic import AfterValidator

from core.exceptions import BadRequestException
from core.i18n import translate as _


def validate_password(value: str) -> str:
    """
    Validates the strength of a password using a regex pattern.

    Ensures the password has at least:
    - 8 characters
    - One uppercase letter
    - One lowercase letter
    - One digit
    - One special character

    Args:
        value (str): The password string to validate.

    Raises:
        BadRequestException: If the password does not meet the required complexity.

    Returns:
        str: The validated password string.
    """
    password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

    if not password_pattern.match(value):
        raise BadRequestException(
            message=_(
                "Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character."
            )
        )

    return value


PasswordValidator = Annotated[str, AfterValidator(validate_password)]
