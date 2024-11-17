import bcrypt


class PasswordHandler:
    @staticmethod
    def hash(password: str) -> str:
        return bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt()).decode()

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password=plain_password.encode(), hashed_password=hashed_password.encode())
