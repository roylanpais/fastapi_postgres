# Models and Database Setup
from sqlalchemy import Column, Integer, String, Text, Float
from pydantic import BaseModel, Field, validator

# Models
class Magazine(Base):
    __tablename__ = "magazines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    base_price = Column(Float, nullable=False)
    discount_quarterly = Column(Float, nullable=False)
    discount_half_yearly = Column(Float, nullable=False)
    discount_annual = Column(Float, nullable=False)

# Schemas
class MagazineBase(BaseModel):
    name: str
    description: str
    base_price: float = Field(..., gt=0, description="Base price must be greater than 0")
    discount_quarterly: float = Field(..., ge=0, le=1, description="Discount must be between 0 and 1")
    discount_half_yearly: float = Field(..., ge=0, le=1, description="Discount must be between 0 and 1")
    discount_annual: float = Field(..., ge=0, le=1, description="Discount must be between 0 and 1")

    @validator("discount_half_yearly", "discount_annual")
    def validate_discounts(cls, value, values, **kwargs):
        if "discount_quarterly" in values and value < values["discount_quarterly"]:
            raise ValueError("Discount must not decrease for longer periods")
        return value

class MagazineCreate(MagazineBase):
    pass

class MagazineUpdate(MagazineBase):
    pass

class MagazineResponse(MagazineBase):
    id: int

    class Config:
        orm_mode = True

# Endpoints for Magazine Management

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/magazines", tags=["magazines"])

@router.post("/", response_model=MagazineResponse)
def create_magazine(magazine: MagazineCreate, db: Session = Depends(get_db)):
    db_magazine = Magazine(**magazine.dict())
    db.add(db_magazine)
    db.commit()
    db.refresh(db_magazine)
    return db_magazine

@router.get("/", response_model=List[MagazineResponse])
def get_magazines(db: Session = Depends(get_db)):
    return db.query(Magazine).all()

@router.get("/{magazine_id}", response_model=MagazineResponse)
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return magazine

@router.put("/{magazine_id}", response_model=MagazineResponse)
def update_magazine(magazine_id: int, magazine: MagazineUpdate, db: Session = Depends(get_db)):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    for key, value in magazine.dict().items():
        setattr(db_magazine, key, value)

    db.commit()
    db.refresh(db_magazine)
    return db_magazine

@router.delete("/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")

    db.delete(magazine)
    db.commit()
    return {"message": "Magazine deleted successfully"}
