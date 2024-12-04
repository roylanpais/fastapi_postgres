from datetime import datetime, timedelta, UTC, date
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.db.base import Base
from app.db.sessions import get_db, engine
# Constants
DATABASE_URL = "postgresql+psycopg2://app_user:app_password@db/app"
SECRET_KEY = "secret key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7

# FastAPI instance
app = FastAPI()


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/")

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)

class Magazine(Base):
    __tablename__ = "magazines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    discount_quarterly = Column(Float, nullable=True)
    discount_half_yearly = Column(Float, nullable=True)
    discount_annual = Column(Float, nullable=True)

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    renewal_period = Column(Integer, nullable=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    magazine_id = Column(Integer, ForeignKey("magazines.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    price = Column(Float, nullable=False)
    next_renewal_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User")
    magazine = relationship("Magazine")
    plan = relationship("Plan")

User.subscriptions = relationship("Subscription", back_populates="user")
Plan.subscriptions = relationship("Subscription", back_populates="plan")

Base.metadata.create_all(bind=engine)

# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class MagazineBase(BaseModel):
    name: str
    description: str
    base_price: float
    discount_quarterly: Optional[float] = None
    discount_half_yearly: Optional[float] = None
    discount_annual: Optional[float] = None

class MagazineCreate(MagazineBase):
    pass

class MagazineUpdate(MagazineBase):
    pass


class PlanBase(BaseModel):
    title: str
    description: str
    renewal_period: int = Field(..., gt=0, description="Renewal period must be greater than 0")

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass

class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    price: float
    next_renewal_date: date

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    is_active: bool




def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# User endpoints
@app.post("/users/register", status_code=200)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/users/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/users/reset-password")
def reset_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = get_password_hash("random_password")
    db.commit()
    return {"message": "Password updated successfully"}

@app.delete("/users/deactivate/{username}")
def deactivate_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = 0
    db.commit()
    return {"message": "User deactivated successfully"}

@app.post("/users/token/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.username})
    refresh_token = create_refresh_token(data={"sub": current_user.username})

    return {"access_token": access_token,  "refresh_token": refresh_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserBase)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Magazine endpoints
@app.get("/magazines/")
def get_magazines(db: Session = Depends(get_db)):
    return db.query(Magazine).all()

@app.post("/magazines/")
def create_magazine(magazine: MagazineCreate, db: Session = Depends(get_db)):
    new_magazine = Magazine(**magazine.model_dump())
    db.add(new_magazine)
    db.commit()
    return {"message": "Magazine created successfully", "id": new_magazine.id, "name": new_magazine.name}

@app.get("/magazines/{magazine_id}")
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return magazine

@app.put("/magazines/{magazine_id}")
def update_magazine(magazine_id: int, magazine: MagazineUpdate, db: Session = Depends(get_db)):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    for key, value in magazine.dict(exclude_unset=True).items():
        setattr(db_magazine, key, value)
    db.commit()
    return {"message": "Magazine updated successfully",  "name": db_magazine.name}

@app.delete("/magazines/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    db.delete(db_magazine)
    db.commit()
    return {"message": "Magazine deleted successfully"}

# Plan endpoints
@app.get("/plans/")
def get_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()

@app.post("/plans/", status_code=200)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    new_plan = Plan(**plan.model_dump())
    db.add(new_plan)
    db.commit()
    return {"message": "Plan created successfully", "id": new_plan.id, "title": new_plan.title, "description": new_plan.description, "renewal_period": new_plan.renewal_period}

@app.get("/plans/{id}")
def get_plan(id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@app.put("/plans/{plan_id}")
def update_plan(plan_id: int, plan: PlanUpdate, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in plan.dict(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    return {"message": "Plan updated successfully", "title": db_plan.title, "description": db_plan.description, "renewal_period": db_plan.renewal_period}

@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan deleted successfully"}

# Subscription endpoints
@app.get("/subscriptions/")
def get_subscriptions(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

@app.post("/subscriptions/")
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    new_subscription = Subscription(**subscription.model_dump())
    db.add(new_subscription)
    db.commit()
    return {"message": "Subscription created successfully", "id": new_subscription.id, "price": new_subscription.price}

@app.get("/subscriptions/{id}")
def get_subscription(id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@app.put("/subscriptions/{subscription_id}")
def update_subscription(subscription_id: int, subscription: SubscriptionUpdate, db: Session = Depends(get_db)):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for key, value in subscription.dict(exclude_unset=True).items():
        setattr(db_subscription, key, value)
    db.commit()
    return {"message": "Subscription updated successfully", "price": db_subscription.price}

@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.is_active = False
    db.commit()
    return {"message": "Subscription deleted successfully"}