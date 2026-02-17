import os


SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me") #TODO - change this later. MUST be changed before production!!!!!!
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "300"))
