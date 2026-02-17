"""Quickstart: CrewAI + AIR — every agent call recorded.

Prerequisites:
    pip install air-sdk crewai langchain-openai
    docker compose up  # start AIR gateway
"""

from crewai import Agent, Task, Crew
from air.integrations.crewai import air_crewai_llm

# Route all LLM calls through AIR
llm = air_crewai_llm("gpt-4o-mini")

researcher = Agent(
    role="AI Safety Researcher",
    goal="Find facts about AI accountability",
    backstory="You are an expert in AI governance.",
    llm=llm,
)

task = Task(
    description="Write a brief on why AI systems need flight recorders.",
    agent=researcher,
    expected_output="A 3-paragraph brief.",
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()

print(result)
# Every LLM call is recorded in AIR with full audit trail
