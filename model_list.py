import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("GOOGLE_API_KEY"))
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("--- Available Models ---")
# We will iterate without filtering to avoid the AttributeError
for model in client.models.list():
    print(f"Name: {model.name}")
    print(f"Display Name: {model.display_name}")
    print("-" * 20)