"""Tests for framework integrations."""

import pytest
from unittest.mock import patch, MagicMock


class TestOpenAIIntegration:
    def test_air_openai_sets_base_url(self):
        mock_cls = MagicMock()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.OpenAI", mock_cls):
                from importlib import reload
                import air.integrations.openai as oai_mod
                reload(oai_mod)
                oai_mod.air_openai(gateway_url="http://air:8080")
                mock_cls.assert_called_once_with(base_url="http://air:8080/v1")

    def test_air_async_openai_sets_base_url(self):
        mock_cls = MagicMock()
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            with patch("openai.AsyncOpenAI", mock_cls):
                from importlib import reload
                import air.integrations.openai as oai_mod
                reload(oai_mod)
                oai_mod.air_async_openai(gateway_url="http://air:8080")
                mock_cls.assert_called_once_with(base_url="http://air:8080/v1")

    def test_air_openai_uses_env(self):
        mock_cls = MagicMock()
        with patch.dict("os.environ", {
            "OPENAI_API_KEY": "sk-test",
            "AIR_GATEWAY_URL": "http://env:9090",
        }):
            with patch("openai.OpenAI", mock_cls):
                from importlib import reload
                import air.integrations.openai as oai_mod
                reload(oai_mod)
                oai_mod.air_openai()
                mock_cls.assert_called_with(base_url="http://env:9090/v1")


class TestLangChainIntegration:
    def test_callback_handler_init(self):
        from air.integrations.langchain import AIRCallbackHandler
        handler = AIRCallbackHandler(gateway_url="http://air:8080")
        assert handler.gateway_url == "http://air:8080"
        assert handler._runs == {}

    def test_callback_tracks_runs(self):
        from air.integrations.langchain import AIRCallbackHandler
        from uuid import uuid4

        handler = AIRCallbackHandler(gateway_url="http://air:8080")
        run_id = uuid4()
        handler.on_llm_start(
            serialized={"kwargs": {"model_name": "gpt-4o"}},
            prompts=["Hello"],
            run_id=run_id,
        )
        assert str(run_id) in handler._runs
        assert handler._runs[str(run_id)]["model"] == "gpt-4o"

    def test_callback_cleans_up_on_error(self):
        from air.integrations.langchain import AIRCallbackHandler
        from uuid import uuid4

        handler = AIRCallbackHandler()
        run_id = uuid4()
        handler._runs[str(run_id)] = {"start_time": 0}
        handler.on_llm_error(Exception("fail"), run_id=run_id)
        assert str(run_id) not in handler._runs


class TestCrewAIIntegration:
    def test_patch_sets_env(self):
        from air.integrations.crewai import patch_crewai
        with patch.dict("os.environ", {}, clear=False):
            patch_crewai(gateway_url="http://air:8080")
            import os
            assert os.environ["OPENAI_API_BASE"] == "http://air:8080/v1"
