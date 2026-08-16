import os

DATABASE_URL = os.getenv("DATABASE_URL", "")
REDIS_URL = os.getenv("REDIS_URL", "")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL", "").rstrip("/")
MODEL_NAME = os.getenv("MODEL_NAME", "")
MODEL_API_KEY = os.getenv("MODEL_API_KEY", "")
