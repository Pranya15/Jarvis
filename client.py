import os
from openai import OpenAI

client = OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
completion = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {
            "role": "system",
            "content": "You are a virtual assistant named Jarvis skilled in general tasks like alexa and google cloud. Give short responses"
        },
        {
            "role": "user",
            "content": "what is coding"
        }
    ]
)

print(completion.choices[0].message.content)