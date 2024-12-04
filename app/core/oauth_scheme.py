from fastapi.security import OAuth2PasswordBearer

#  OAuth2 setup
# Define OAuth2PasswordBearer with scopes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")