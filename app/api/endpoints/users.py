from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.schemas.users import UserCreate, UserBase, UserLogin
from app.db.models import User
from app.utils import get_password_hash, create_access_token, create_refresh_token, verify_password, get_current_user
from pydantic import EmailStr

router = APIRouter()


@router.post("/register", status_code=200)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(user.hashed_password, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/reset-password")
def reset_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash("random_password")
    db.commit()
    return {"message": "Password updated successfully"}

@router.delete("/deactivate/{username}")
def deactivate_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User deactivated successfully"}

@router.post("/token/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.username})
    refresh_token = create_refresh_token(data={"sub": current_user.username})

    return {"access_token": access_token,  "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/me", response_model=UserBase)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
