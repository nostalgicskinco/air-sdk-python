"""Core AIR client — wraps any OpenAI-compatible provider through the gateway."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx


@dataclass
class AIRConfig:
    """Configuration for the AIR gateway connection."""

    gateway_url: str = "http://localhost:8080"
    api_key: str = ""
    timeout: float = 120.0
    verify_ssl: bool = True
    extra_headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "AIRConfig":
        return cls(
            gateway_url=os.getenv("AIR_GATEWAY_URL", "http://localhost:8080"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            timeout=float(os.getenv("AIR_TIMEOUT", "120")),
        )


class AIRClient:
    """HTTP client that talks to the AIR Blackbox Gateway.

    Use this directly for low-level access, or use the framework
    integrations (air.integrations.openai, .langchain, .crewai)
    for drop-in recording.
    """

    def __init__(self, config: Optional[AIRConfig] = None):
        self.config = config or AIRConfig.from_env()
        self._http = httpx.Client(
            base_url=self.config.gateway_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
        )

    def chat(self, messages: list[dict], model: str = "gpt-4o-mini",
             **kwargs: Any) -> dict:
        """Send a chat completion through the gateway."""
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            **self.config.extra_headers,
        }
        payload = {"model": model, "messages": messages, **kwargs}
        resp = self._http.post("/v1/chat/completions",
                               json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        data["_air"] = {
            "run_id": resp.headers.get("x-run-id", ""),
            "gateway": self.config.gateway_url,
        }
        return data

    def health(self) -> dict:
        """Check gateway health."""
        resp = self._http.get("/health")
        resp.raise_for_status()
        return resp.json()

    def audit(self, gateway_key: str = "") -> dict:
        """Get audit chain status and compliance report."""
        headers = {}
        if gateway_key:
            headers["X-Gateway-Key"] = gateway_key
        resp = self._http.get("/v1/audit", headers=headers)
        resp.raise_for_status()
        return resp.json()

    def export_evidence(self, gateway_key: str = "") -> dict:
        """Export signed evidence package."""
        headers = {}
        if gateway_key:
            headers["X-Gateway-Key"] = gateway_key
        resp = self._http.get("/v1/audit/export", headers=headers)
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
