from passlib.context import CryptContext

# Constants
DATABASE_URL = "postgresql+psycopg2://app_user:app_password@db/app"
SECRET_KEY = "secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
