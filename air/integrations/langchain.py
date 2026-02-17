"""LangChain callback handler that records all LLM calls through AIR.

Usage:
    from langchain_openai import ChatOpenAI
    from air.integrations.langchain import AIRCallbackHandler

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        callbacks=[AIRCallbackHandler()]
    )
    llm.invoke("What is a flight recorder?")
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional
from uuid import UUID

import httpx


class AIRCallbackHandler:
    """LangChain callback handler that logs LLM interactions to AIR gateway."""

    def __init__(self, gateway_url: str | None = None):
        self.gateway_url = gateway_url or os.getenv(
            "AIR_GATEWAY_URL", "http://localhost:8080"
        )
        self._runs: dict[str, dict] = {}
        self._http = httpx.Client(base_url=self.gateway_url, timeout=30)

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str],
        *, run_id: UUID, **kwargs: Any
    ) -> None:
        """Record the start of an LLM call."""
        self._runs[str(run_id)] = {
            "start_time": time.time(),
            "model": serialized.get("kwargs", {}).get("model_name", "unknown"),
            "prompts": prompts,
        }

    def on_llm_end(self, response: Any, *, run_id: UUID, **kwargs: Any) -> None:
        """Record the completion of an LLM call."""
        run_data = self._runs.pop(str(run_id), {})
        duration_ms = int((time.time() - run_data.get("start_time", 0)) * 1000)

        # Extract generation info
        generations = []
        if hasattr(response, "generations"):
            for gen_list in response.generations:
                for gen in gen_list:
                    generations.append(gen.text if hasattr(gen, "text") else str(gen))

        # Post event to AIR episode store
        try:
            self._http.post(
                "/v1/episodes",
                json={
                    "agent_id": "langchain",
                    "task": run_data.get("prompts", [""])[0][:200],
                    "steps": [
                        {
                            "type": "llm_call",
                            "model": run_data.get("model", "unknown"),
                            "input": run_data.get("prompts", []),
                            "output": generations,
                            "duration_ms": duration_ms,
                        }
                    ],
                    "status": "completed",
                },
            )
        except Exception:
            pass  # Non-blocking: never fail the LLM call

    def on_llm_error(self, error: Exception, *, run_id: UUID, **kwargs: Any) -> None:
        """Record LLM errors."""
        self._runs.pop(str(run_id), None)


def air_langchain_llm(model: str = "gpt-4o-mini", gateway_url: str | None = None,
                       **kwargs: Any):
    """Create a LangChain ChatOpenAI that routes through AIR.

    Usage:
        from air.integrations.langchain import air_langchain_llm
        llm = air_langchain_llm("gpt-4o-mini")
        llm.invoke("What is a flight recorder?")
    """
    from langchain_openai import ChatOpenAI

    url = gateway_url or os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
    return ChatOpenAI(
        model=model,
        base_url=url + "/v1",
        callbacks=[AIRCallbackHandler(gateway_url=url)],
        **kwargs,
    )
