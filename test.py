import os
from openai import OpenAI

print("API Key Found?", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hi in 3 words."}],
)
print(resp.choices[0].message.content)
