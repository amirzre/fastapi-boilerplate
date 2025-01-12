from typing import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi import Request

from core.i18n import TranslationWrapper, set_locale, translate, translate_with_variables


class TestTranslationWrapper:
    @pytest.fixture
    def reset_singleton(self) -> Generator[None, None, None]:
        """Fixture to reset the TranslationWrapper singleton between tests."""
        TranslationWrapper._instance = None
        yield
        TranslationWrapper._instance = None

    @pytest.fixture
    def mock_request(self) -> Mock:
        """Fixture to create a mock FastAPI request object."""
        request = Mock(spec=Request)
        request.headers = {}
        request.cookies = {}
        request.query_params = {}
        return request

    def test_singleton_pattern(self, reset_singleton: None) -> None:
        """Test that TranslationWrapper implements the singleton pattern correctly."""
        instance1 = TranslationWrapper()
        instance2 = TranslationWrapper()

        assert instance1 is instance2
        assert TranslationWrapper._instance is instance1

    def test_init_translation_default_language(self, reset_singleton: None) -> None:
        """Test translation initialization with default language."""
        wrapper = TranslationWrapper()
        assert wrapper.translations is not None
        assert hasattr(wrapper.translations, "gettext")

    @pytest.mark.parametrize(
        "message,expected",
        [
            ("Hello", "سلام"),
            ("Goodbye", "خداحافظ"),
            ("Welcome", "خوش آمدید"),
        ],
    )
    def test_basic_translation(self, reset_singleton: None, message: str, expected: str) -> None:
        """Test basic translation functionality with different messages."""
        wrapper = TranslationWrapper()
        with patch.object(wrapper.translations, "gettext", return_value=expected):
            result = wrapper.gettext(message)

            assert result == expected

    @pytest.mark.asyncio
    async def test_set_locale_from_query_params(self, mock_request: Mock) -> None:
        """Test locale setting from query parameters."""
        mock_request.query_params = {"lang": "fa"}
        await set_locale(mock_request)

        wrapper = TranslationWrapper()
        assert wrapper.translations is not None

    @pytest.mark.asyncio
    async def test_set_locale_from_cookies(self, mock_request: Mock) -> None:
        """Test locale setting from cookies."""
        mock_request.cookies = {"Accept-Language": "fa"}
        await set_locale(mock_request)

        wrapper = TranslationWrapper()
        assert wrapper.translations is not None

    @pytest.mark.asyncio
    async def test_set_locale_from_headers(self, mock_request: Mock) -> None:
        """Test locale setting from headers."""
        mock_request.headers = {"Accept-Language": "fa,en;q=0.9"}
        await set_locale(mock_request)

        wrapper = TranslationWrapper()
        assert wrapper.translations is not None

    def test_translate_helper_function(self, reset_singleton: None) -> None:
        """
        Test the translate helper function.
        """
        expected = "Translated text"
        with patch.object(TranslationWrapper, "gettext", return_value=expected):
            result = translate("Hello")

            assert result == expected

    def test_translate_with_variables(self, reset_singleton: None) -> None:
        """Test translation with variable substitution."""
        template = "Hello, {name}!"
        translated_template = "سلام, {name}!"
        expected = "سلام, John!"

        with patch("core.i18n.base.translate", return_value=translated_template):
            result = translate_with_variables(template, name="John")

            assert result == expected

    def test_translation_fallback(self, reset_singleton: None) -> None:
        """Test fallback behavior when translation is not available."""
        original_message = "This should fallback to English"
        wrapper = TranslationWrapper()

        with patch("gettext.translation") as mock_translation:
            mock_translation.side_effect = FileNotFoundError
            result = wrapper.gettext(original_message)

            assert result == original_message
