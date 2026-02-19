import os
from google import genai
from google.genai import types
import json

# Check for API key
if "GOOGLE_API_KEY" not in os.environ:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit(1)

# Initialize the new client
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return None

# Load inputs
prd_content = read_file("prd.txt")
code_content = read_file("code_submission.py")
system_prompt = read_file("system_prompt.txt")

if not prd_content or not code_content or not system_prompt:
    exit(1)

# Combine user content (system prompt goes in config)
user_prompt = f"""
PRD:
{prd_content}

---
CODE SUBMISSION:
{code_content}
"""

print("Analyzing code against PRD...")

try:
    # Call API with system instruction in config
    response = client.models.generate_content(
        model='models/gemini-2.5-flash',          # or 'models/gemini-1.5-flash' if needed
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        )
    )

    # Extract JSON from response
    text = response.text
    start = text.find('{')
    end = text.rfind('}') + 1
    if start != -1 and end != -1:
        json_str = text[start:end]
        report = json.loads(json_str)

        with open("compliance_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print("Compliance report generated: compliance_report.json")
        print(json.dumps(report, indent=2))
    else:
        print("Error: No JSON found in response.")
        print("Raw response:", text)

except Exception as e:
    print(f"An error occurred: {e}")