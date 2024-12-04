from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.db.models import Magazine
from app.schemas.magazines import MagazineCreate, MagazineUpdate

router = APIRouter()


# Magazine endpoints
@router.get("/")
def get_magazines(db: Session = Depends(get_db)):
    return db.query(Magazine).all()

@router.post("/")
def create_magazine(magazine: MagazineCreate, db: Session = Depends(get_db)):
    new_magazine = Magazine(**magazine.model_dump())
    db.add(new_magazine)
    db.commit()
    return {"message": "Magazine created successfully", "id": new_magazine.id, "name": new_magazine.name}

@router.get("/{magazine_id}")
def get_magazine(magazine_id: int, db: Session = Depends(get_db)):
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return magazine

@router.put("/{magazine_id}")
def update_magazine(magazine_id: int, magazine: MagazineUpdate, db: Session = Depends(get_db)):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    for key, value in magazine.model_dump(exclude_unset=True).items():
        setattr(db_magazine, key, value)
    db.commit()
    return {"message": "Magazine updated successfully",  "name": db_magazine.name}

@router.delete("/{magazine_id}")
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    db.delete(db_magazine)
    db.commit()
    return {"message": "Magazine deleted successfully"}

