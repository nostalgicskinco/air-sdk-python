"""OpenAI SDK integration — zero-code recording through AIR.

Usage (one-liner):
    from openai import OpenAI
    from air.integrations.openai import air_openai

    client = air_openai()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(resp.choices[0].message.content)
    # Recorded through AIR with full audit trail.

Usage (wrap existing client):
    from openai import OpenAI
    import air

    client = air.air_wrap(OpenAI())
"""

from __future__ import annotations

import os
from typing import Any


def air_openai(gateway_url: str | None = None, **kwargs: Any):
    """Create an OpenAI client routed through AIR gateway.

    This is the simplest integration — just use this instead of OpenAI().
    All calls are automatically recorded with tamper-evident audit trails.
    """
    from openai import OpenAI

    url = gateway_url or os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
    return OpenAI(base_url=url + "/v1", **kwargs)


def air_async_openai(gateway_url: str | None = None, **kwargs: Any):
    """Create an async OpenAI client routed through AIR gateway."""
    from openai import AsyncOpenAI

    url = gateway_url or os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
    return AsyncOpenAI(base_url=url + "/v1", **kwargs)
