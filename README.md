# AIR SDK for Python

[![CI](https://github.com/nostalgicskinco/air-sdk-python/actions/workflows/ci.yml/badge.svg)](https://github.com/nostalgicskinco/air-sdk-python/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

**Record every AI decision your agents make. One line of code.**

AIR SDK connects your Python AI applications to the [AIR Blackbox Gateway](https://github.com/nostalgicskinco/air-blackbox-gateway) — giving you tamper-evident audit trails, compliance reporting, and deterministic replay without changing how you write code.

## Install

```bash
pip install air-sdk
```

With framework extras:
```bash
pip install air-sdk[openai]      # OpenAI integration
pip install air-sdk[langchain]   # LangChain integration
pip install air-sdk[crewai]      # CrewAI integration
pip install air-sdk[all]         # Everything
```

## Quickstart

### OpenAI (3 lines)

```python
from openai import OpenAI
import air

client = air.air_wrap(OpenAI())

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is a flight recorder?"}],
)
print(response.choices[0].message.content)
# Every call recorded with tamper-evident audit trail
```

### LangChain (2 lines)

```python
from air.integrations.langchain import air_langchain_llm

llm = air_langchain_llm("gpt-4o-mini")
response = llm.invoke("Explain tamper-evident logging.")
print(response.content)
# Works with chains, agents, and tools
```

### CrewAI (swap one import)

```python
from crewai import Agent, Task, Crew
from air.integrations.crewai import air_crewai_llm

llm = air_crewai_llm("gpt-4o-mini")
agent = Agent(role="Researcher", goal="Find facts", llm=llm)
task = Task(description="Research AI safety", agent=agent,
            expected_output="A brief report.")
crew = Crew(agents=[agent], tasks=[task])
crew.kickoff()
# Every agent LLM call recorded in AIR
```

### Direct Client

```python
from air import AIRClient

with AIRClient() as client:
    # Chat through the gateway
    result = client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4o-mini",
    )
    print(result["_air"]["run_id"])  # Your audit trail ID

    # Check compliance status
    audit = client.audit(gateway_key="your-key")

    # Export signed evidence for regulators
    evidence = client.export_evidence(gateway_key="your-key")
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `AIR_GATEWAY_URL` | `http://localhost:8080` | AIR gateway URL |
| `OPENAI_API_KEY` | *(none)* | Your LLM provider API key |
| `AIR_TIMEOUT` | `120` | Request timeout in seconds |

## What You Get

When your code runs through AIR, every LLM call automatically gets:

- **Tamper-evident audit trail** — HMAC-SHA256 chain, modify one record and the chain breaks
- **Vault-backed content** — prompts and completions in your S3/MinIO, not third-party clouds
- **Compliance reporting** — 22 controls across SOC 2 and ISO 27001, auto-evaluated
- **Signed evidence export** — hand your auditor a single JSON document
- **Deterministic replay** — reproduce any AI decision from the audit record

## Part of the AIR Ecosystem

This SDK is the developer entry point to the [AIR Blackbox Gateway](https://github.com/nostalgicskinco/air-blackbox-gateway) infrastructure:

| Component | What It Does |
|---|---|
| **air-sdk-python** (this repo) | Python integrations for OpenAI, LangChain, CrewAI |
| [air-blackbox-gateway](https://github.com/nostalgicskinco/air-blackbox-gateway) | Core proxy + vault + audit chain + compliance |
| [air-platform](https://github.com/nostalgicskinco/air-platform) | Docker Compose orchestration |
| [agent-episode-store](https://github.com/nostalgicskinco/agent-episode-store) | Episode-level audit grouping |
| [agent-policy-engine](https://github.com/nostalgicskinco/agent-policy-engine) | Risk-tiered autonomy + runtime policy |

## License

Apache-2.0
