import re
from typing import Annotated

from pydantic import AfterValidator

from core.exceptions import BadRequestException
from core.i18n import translate as _


def validate_password(value: str) -> str:
    """Validate password to ensure it meets the required complexity."""
    password_pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

    if not password_pattern.match(value):
        raise BadRequestException(
            message=_(
                "Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character."
            )
        )

    return value


PasswordValidator = Annotated[str, AfterValidator(validate_password)]
