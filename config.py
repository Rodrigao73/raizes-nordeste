from passlib.context import CryptContext
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))

bcrypt_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth_schema = HTTPBearer()