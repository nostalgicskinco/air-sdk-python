"""Tests for AIR SDK core client."""

import json
import pytest
from unittest.mock import patch, MagicMock

from air.client import AIRClient, AIRConfig


class TestAIRConfig:
    def test_defaults(self):
        cfg = AIRConfig()
        assert cfg.gateway_url == "http://localhost:8080"
        assert cfg.timeout == 120.0
        assert cfg.verify_ssl is True

    def test_from_env(self):
        with patch.dict("os.environ", {
            "AIR_GATEWAY_URL": "http://air:9090",
            "OPENAI_API_KEY": "sk-test",
            "AIR_TIMEOUT": "30",
        }):
            cfg = AIRConfig.from_env()
            assert cfg.gateway_url == "http://air:9090"
            assert cfg.api_key == "sk-test"
            assert cfg.timeout == 30.0

    def test_custom(self):
        cfg = AIRConfig(gateway_url="http://custom:1234", api_key="key")
        assert cfg.gateway_url == "http://custom:1234"


class TestAIRClient:
    def test_context_manager(self):
        cfg = AIRConfig(api_key="test")
        with AIRClient(cfg) as client:
            assert client.config.api_key == "test"

    def test_chat_builds_payload(self):
        cfg = AIRConfig(api_key="sk-test")
        client = AIRClient(cfg)
        # Mock the httpx client
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Hello"}}]
        }
        mock_resp.headers = {"x-run-id": "run-123"}
        mock_resp.raise_for_status = MagicMock()
        client._http.post = MagicMock(return_value=mock_resp)

        result = client.chat(
            messages=[{"role": "user", "content": "Hi"}],
            model="gpt-4o-mini",
        )

        # Verify the call was made correctly
        call_args = client._http.post.call_args
        assert call_args[0][0] == "/v1/chat/completions"
        payload = call_args[1]["json"]
        assert payload["model"] == "gpt-4o-mini"
        assert payload["messages"][0]["content"] == "Hi"

        # Verify AIR metadata is attached
        assert result["_air"]["run_id"] == "run-123"
        client.close()

    def test_health_endpoint(self):
        cfg = AIRConfig()
        client = AIRClient(cfg)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ok"}
        mock_resp.raise_for_status = MagicMock()
        client._http.get = MagicMock(return_value=mock_resp)

        result = client.health()
        assert result["status"] == "ok"
        client._http.get.assert_called_with("/health")
        client.close()

    def test_audit_with_key(self):
        cfg = AIRConfig()
        client = AIRClient(cfg)
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"chain_length": 42}
        mock_resp.raise_for_status = MagicMock()
        client._http.get = MagicMock(return_value=mock_resp)

        result = client.audit(gateway_key="secret")
        call_args = client._http.get.call_args
        assert call_args[1]["headers"]["X-Gateway-Key"] == "secret"
        assert result["chain_length"] == 42
        client.close()
