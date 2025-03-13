import os

from dotenv import load_dotenv

load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("DEBUG: OPENAI_API_KEY =", OPENAI_API_KEY)