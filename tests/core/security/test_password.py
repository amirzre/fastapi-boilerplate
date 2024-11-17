import pytest

from core.security import PasswordHandler


class TestPasswordHandler:
    def test_hash_creates_different_hashes_for_same_password(self):
        """
        Ensure hashing the same password twice results in different hashes.
        """
        password = "test_password"
        hash1 = PasswordHandler.hash(password)
        hash2 = PasswordHandler.hash(password)
        assert hash1 != hash2, "Hashes for the same password should be unique."

    def test_verify_correct_password(self):
        """
        Ensure the verify method returns True for a correct password.
        """
        password = "correct_password"
        hashed_password = PasswordHandler.hash(password)
        assert PasswordHandler.verify(hashed_password, password), "Verification failed for the correct password."

    def test_verify_incorrect_password(self):
        """
        Ensure the verify method returns False for an incorrect password.
        """
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed_password = PasswordHandler.hash(password)
        assert not PasswordHandler.verify(
            hashed_password, wrong_password
        ), "Verification passed for an incorrect password."

    def test_verify_with_normalized_hash(self):
        """
        Ensure the verify method can handle a normalized bcrypt hash.
        """
        password = "test_password"
        normalized_hash = PasswordHandler.pwd_context.hash(password)  # Simulate normalization
        assert PasswordHandler.verify(normalized_hash, password), "Verification failed with a normalized hash."

    def test_hashing_empty_password(self):
        """
        Ensure hashing an empty password does not raise errors and generates a hash.
        """
        password = ""
        hashed_password = PasswordHandler.hash(password)
        assert (
            isinstance(hashed_password, str) and hashed_password
        ), "Hashing an empty password should produce a valid hash."

    def test_verify_empty_password(self):
        """
        Ensure verifying an empty password works as expected.
        """
        password = ""
        hashed_password = PasswordHandler.hash(password)
        assert PasswordHandler.verify(hashed_password, password), "Verification failed for an empty password."

    def test_verify_invalid_hash_format(self):
        """
        Ensure the verify method handles invalid hash formats gracefully.
        """
        password = "password"
        invalid_hash = "invalid_hash_format"
        with pytest.raises(ValueError):
            PasswordHandler.verify(invalid_hash, password)

    def test_hash_length(self):
        """
        Ensure the generated hash has a reasonable length.
        """
        password = "test_password"
        hashed_password = PasswordHandler.hash(password)
        assert len(hashed_password) > 50, "Hash length is unexpectedly short."
