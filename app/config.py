import os
from dotenv import load_dotenv

# Load semua variabel dari file .env
load_dotenv()

# Akses variabel lingkungan
DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validasi awal
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables.")
if not OPENROUTER_API_KEY:
    print("⚠️ Warning: OPENROUTER_API_KEY not found (AI features will be disabled).")
