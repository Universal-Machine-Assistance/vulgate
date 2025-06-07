import os, sys
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID") or None
)

try:
    reply = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Respond with just the word PONG"}],
        max_tokens=5,
        temperature=0.0,
    )
    print("✅ OpenAI call succeeded:", reply.choices[0].message.content.strip())
except Exception as e:
    print("❌ OpenAI call failed:", e)
    sys.exit(1)
