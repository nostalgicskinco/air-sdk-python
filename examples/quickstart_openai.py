"""Quickstart: OpenAI + AIR in 3 lines.

Prerequisites:
    pip install air-sdk openai
    docker compose up  # start AIR gateway
"""

from openai import OpenAI
import air

# One line: wrap your existing client
client = air.air_wrap(OpenAI())

# Use it exactly like normal — every call is now recorded
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is a flight recorder?"}],
)

print(response.choices[0].message.content)
# Check x-run-id in AIR for the audit trail
