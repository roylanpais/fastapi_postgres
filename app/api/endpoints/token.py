from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.db.models import User
from app.utils import create_access_token, create_refresh_token, verify_password

router = APIRouter()


@router.post("/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    password_verified = verify_password(user.hashed_password, form_data.password)
    if not user or not password_verified:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}