"""Tests for air_wrap one-liner."""

import pytest
from unittest.mock import MagicMock, patch

from air.wrapper import air_wrap


class TestAirWrap:
    def test_wraps_openai_client(self):
        """Simulate wrapping an OpenAI client."""
        mock_client = MagicMock()
        mock_client.base_url = "https://api.openai.com/v1"

        result = air_wrap(mock_client, gateway_url="http://air:8080")
        # Should return the same client object
        assert result is mock_client

    def test_wraps_nested_client(self):
        """Wraps client with nested _client attribute."""
        inner = MagicMock()
        inner.base_url = "https://api.openai.com/v1"
        outer = MagicMock(spec=[])  # no base_url
        outer._client = inner

        result = air_wrap(outer, gateway_url="http://air:8080")
        assert result is outer

    def test_rejects_unwrappable(self):
        """Raises TypeError for unsupported clients."""
        obj = object()
        with pytest.raises(TypeError, match="Cannot wrap"):
            air_wrap(obj)

    def test_uses_env_default(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://api.openai.com/v1"

        with patch.dict("os.environ", {"AIR_GATEWAY_URL": "http://env:9090"}):
            air_wrap(mock_client)
