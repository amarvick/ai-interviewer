import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", ""))

# AI Interview configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_CHAT = os.getenv("GEMINI_MODEL_CHAT", "")
INTERVIEW_AI_MODE = os.getenv("INTERVIEW_AI_MODE", "strict").strip().lower()
