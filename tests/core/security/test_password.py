import pytest

from core.security import PasswordHandler


class TestPasswordHandler:
    @pytest.fixture
    def plain_password(self):
        return "SecurePassword123!"

    def test_hash_generates_valid_hash(self, plain_password):
        """
        Test that the hash method generates a non-empty hash string.
        """
        hashed_password = PasswordHandler.hash(plain_password)
        assert isinstance(hashed_password, str)
        assert hashed_password != ""
        assert len(hashed_password) > len(plain_password)

    def test_verify_with_valid_password(self, plain_password):
        """
        Test that verify returns True for a valid password and its hash.
        """
        hashed_password = PasswordHandler.hash(plain_password)
        assert PasswordHandler.verify(plain_password, hashed_password)

    def test_verify_with_invalid_password(self, plain_password):
        """
        Test that verify returns False for an invalid password.
        """
        hashed_password = PasswordHandler.hash(plain_password)
        invalid_password = "WrongPassword!"
        assert not PasswordHandler.verify(invalid_password, hashed_password)

    def test_hash_is_different_each_time(self, plain_password):
        """
        Test that the hash method generates a different hash each time for the same input.
        """
        hashed_password_1 = PasswordHandler.hash(plain_password)
        hashed_password_2 = PasswordHandler.hash(plain_password)
        assert hashed_password_1 != hashed_password_2

    def test_hash_is_secure(self, plain_password):
        """
        Test that the hash does not contain the original password.
        """
        hashed_password = PasswordHandler.hash(plain_password)
        assert plain_password not in hashed_password
