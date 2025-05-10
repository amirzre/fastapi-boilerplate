from datetime import datetime, timedelta, timezone

import jwt
import pytest

from core.security.jwt import JWTDecodeError, JWTExpiredError, JWTHandler


class TestJWTHandler:
    @pytest.fixture
    def payload(self):
        return {"user_id": 1, "role": "user"}

    def test_encode_creates_valid_jwt(self, payload):
        """
        Test that encode generates a valid JWT with the correct payload and expiration.
        """
        token = JWTHandler.encode(payload)
        decoded = jwt.decode(token, key=JWTHandler.secret_key, algorithms=[JWTHandler.algorithm])
        assert "user_id" in decoded and decoded["user_id"] == payload["user_id"]
        assert "role" in decoded and decoded["role"] == payload["role"]
        assert "exp" in decoded

    def test_encode_refresh_token_creates_valid_jwt(self, payload):
        """
        Test that encode_refresh_token generates a valid JWT with a longer expiration.
        """
        token = JWTHandler.encode_refresh_token(payload)
        decoded = jwt.decode(token, key=JWTHandler.secret_key, algorithms=[JWTHandler.algorithm])
        assert "user_id" in decoded and decoded["user_id"] == payload["user_id"]
        assert "role" in decoded and decoded["role"] == payload["role"]
        assert "exp" in decoded

    def test_decode_valid_token(self, payload):
        """
        Test that a valid token can be decoded successfully.
        """
        token = JWTHandler.encode(payload)
        decoded = JWTHandler.decode(token)
        assert decoded["user_id"] == payload["user_id"]
        assert decoded["role"] == payload["role"]

    def test_decode_expired_token(self, payload):
        """
        Test that decoding an expired token raises JWTExpiredError.
        """
        token = jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )
        with pytest.raises(JWTExpiredError):
            JWTHandler.decode(token)

    def test_decode_invalid_token(self):
        """
        Test that decoding an invalid token raises JWTDecodeError.
        """
        invalid_token = "invalid.token.value"
        with pytest.raises(JWTDecodeError):
            JWTHandler.decode(invalid_token)

    def test_decode_expired_token_with_skip_verification(self, payload):
        """
        Test that decode_expired works and skips expiration verification.
        """
        token = jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )
        decoded = JWTHandler.decode_expired(token)
        assert decoded["user_id"] == payload["user_id"]
        assert decoded["role"] == payload["role"]

    def test_token_expiration_with_valid_token(self, payload):
        """
        Test that token_expiration returns the correct expiration for a valid token.
        """
        token = JWTHandler.encode(payload)
        expiration = JWTHandler.token_expiration(token)
        assert isinstance(expiration, datetime)
        assert expiration > datetime.now(timezone.utc)

    def test_token_expiration_with_expired_token(self, payload):
        """
        Test that token_expiration raises JWTExpiredError for an expired token.
        """
        token = jwt.encode(
            {**payload, "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            key=JWTHandler.secret_key,
            algorithm=JWTHandler.algorithm,
        )
        with pytest.raises(JWTExpiredError):
            JWTHandler.token_expiration(token)

    def test_token_expiration_with_invalid_token(self):
        """
        Test that token_expiration raises JWTDecodeError for an invalid token.
        """
        invalid_token = "invalid.token.value"
        with pytest.raises(JWTDecodeError):
            JWTHandler.token_expiration(invalid_token)
