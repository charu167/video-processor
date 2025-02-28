import os
from pathlib import Path
import dotenv

BASE_DIR = Path(__file__).resolve().parent  # Directory of this script
dotenv_file = BASE_DIR.parent / ".env"      # Parent folder of script
dotenv.load_dotenv(dotenv_file)



REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")