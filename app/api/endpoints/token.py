from fastapi.security import OAuth2PasswordBearer

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/")