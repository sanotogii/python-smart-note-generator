import os
from dotenv import load_dotenv
from pathlib import Path

# Get the directory containing this file
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

# Get environment variables with error handling
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Get notes directory with default fallback
NOTES_OUTPUT_DIR = os.getenv('NOTES_OUTPUT_DIR', str(BASE_DIR / 'notes'))

# Convert to proper path and create if doesn't exist
NOTES_OUTPUT_DIR = Path(NOTES_OUTPUT_DIR)
NOTES_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"Config loaded - API Key present: {bool(GEMINI_API_KEY)}")
print(f"Notes directory: {NOTES_OUTPUT_DIR}")
