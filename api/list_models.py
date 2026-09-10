import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

for model in client.models.list():
    print(model.name, "-", model.supported_actions)