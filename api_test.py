import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
org_id = os.getenv("OPENAI_ORG_ID")
project_id = os.getenv("OPENAI_PROJECT_ID")  # Project ID

# Debugging: Print loaded keys
print(f"🔹 API Key Loaded: {api_key[:10]}... (masked for security)")
print(f"🔹 Organization ID Loaded: {org_id}")
print(f"🔹 Project ID Loaded: {project_id}")

# Set OpenAI credentials correctly
openai.api_key = api_key
openai.organization = org_id  

try:
    # List available models 
    models = openai.models.list()

    print("✅ API Key is working! Available models:")
    for model in models.data:
        print(model.id)
except openai.AuthenticationError:
    print("❌ Incorrect API Key! Check your API key and organization ID.")
except openai.OpenAIError as e:
    print(f"❌ OpenAI API Error: {e}")
