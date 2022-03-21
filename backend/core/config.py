import os
from dotenv import load_dotenv

from pathlib import Path

from core.hashing import Hasher

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "Users"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM = "HS256"  # new
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins

    FIRST_USER_PASSWORD = os.getenv("FIRST_USER_PASSWORD")

    INITIAL_DATA = {
        'users': [
            {
                'username': os.getenv('FIRST_USER_NAME'),
                'email': os.getenv('FIRST_USER_EMAIL'),
                'hashed_password': Hasher.get_password_hash(FIRST_USER_PASSWORD),
                'is_active': True,
                'is_superuser': True,
            },
        ],
    }


settings = Settings()
