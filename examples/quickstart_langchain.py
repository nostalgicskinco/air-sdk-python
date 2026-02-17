"""Quickstart: LangChain + AIR in 2 lines.

Prerequisites:
    pip install air-sdk langchain-openai
    docker compose up  # start AIR gateway
"""

from air.integrations.langchain import air_langchain_llm

# One line: get a LangChain LLM routed through AIR
llm = air_langchain_llm("gpt-4o-mini")

# Use it like any LangChain LLM
response = llm.invoke("What is a flight recorder?")
print(response.content)

# Works with chains too
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{question}"),
])

chain = prompt | llm
result = chain.invoke({"question": "Explain tamper-evident logging."})
print(result.content)
