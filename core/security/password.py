import bcrypt


class PasswordHandler:
    """
    Handles password hashing and verification using bcrypt.

    Provides static methods for securely hashing passwords and verifying
    plain-text passwords against hashed versions.
    """

    @staticmethod
    def hash(password: str) -> str:
        """
        Hashes a plain-text password using bcrypt.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: A bcrypt-hashed password string.
        """
        return bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt()).decode()

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a plain-text password against a hashed password.

        Args:
            plain_password (str): The plain-text password to verify.
            hashed_password (str): The previously hashed password for comparison.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password=plain_password.encode(), hashed_password=hashed_password.encode())
