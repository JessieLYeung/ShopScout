from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
db_url = os.getenv("DATABASE_URL")

debug_mode = os.getenv("DEBUG", "False")