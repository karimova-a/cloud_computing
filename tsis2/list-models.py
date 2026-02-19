from google import genai
import os

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
print("Available models that support generateContent:\n")
for model in client.models.list():
    if 'generateContent' in model.supported_actions:
        print(f"- {model.name}")