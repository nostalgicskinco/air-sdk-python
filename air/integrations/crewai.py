"""CrewAI integration — route all agent LLM calls through AIR gateway.

Usage:
    from crewai import Agent, Task, Crew
    from air.integrations.crewai import air_crewai_llm

    llm = air_crewai_llm("gpt-4o-mini")
    agent = Agent(role="Researcher", goal="Find facts", llm=llm)
    task = Task(description="Research AI safety", agent=agent)
    crew = Crew(agents=[agent], tasks=[task])
    crew.kickoff()
    # Every LLM call is now recorded in AIR.
"""

from __future__ import annotations

import os
from typing import Any, Optional


def air_crewai_llm(model: str = "gpt-4o-mini",
                    gateway_url: str | None = None,
                    **kwargs: Any):
    """Create a LangChain ChatOpenAI compatible with CrewAI, routed through AIR.

    CrewAI uses LangChain under the hood, so we return a ChatOpenAI
    pointed at the AIR gateway.
    """
    from langchain_openai import ChatOpenAI
    from air.integrations.langchain import AIRCallbackHandler

    url = gateway_url or os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
    return ChatOpenAI(
        model=model,
        base_url=url + "/v1",
        callbacks=[AIRCallbackHandler(gateway_url=url)],
        **kwargs,
    )


def patch_crewai(gateway_url: str | None = None) -> None:
    """Monkey-patch CrewAI's default LLM to route through AIR.

    Call this once at startup:
        import air.integrations.crewai
        air.integrations.crewai.patch_crewai()

    All CrewAI agents will then use AIR automatically.
    """
    url = gateway_url or os.getenv("AIR_GATEWAY_URL", "http://localhost:8080")
    os.environ["OPENAI_API_BASE"] = url + "/v1"
