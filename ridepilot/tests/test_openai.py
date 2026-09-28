import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

print("API key loaded:", bool(api_key))

client = OpenAI(api_key=api_key)

# Blocking this test since there is no credit in open AI iti s getting failed
'''
response = client.responses.create(
    model="gpt-5.6-luna",
    input="Say hello to RidePilot in one sentence."
)

print(response.output_text)
'''