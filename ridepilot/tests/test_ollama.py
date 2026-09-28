from ollama import chat


response = chat(
    model="gpt-oss:20b",
    messages=[
        {
            "role": "user",
            "content": "Say hello to RidePilot in one sentence."
        }
    ]
)

print(response.message.content)
