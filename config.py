from dotenv import load_dotenv
import os

# Load environment variables from a .env file (if present)
load_dotenv()

# GROQ API key and model name. These will default to the hardcoded
# values but can be overridden via environment variables.
GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    "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",
)

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
