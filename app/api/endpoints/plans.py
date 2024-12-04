from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.db.models import Plan
from app.schemas.plans import PlanCreate, PlanUpdate

router = APIRouter()

# Plan endpoints
@router.get("/")
def get_plans(db: Session = Depends(get_db)):
    return db.query(Plan).all()

@router.post("/", status_code=200)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    new_plan = Plan(**plan.model_dump())
    db.add(new_plan)
    db.commit()
    return {"message": "Plan created successfully", "id": new_plan.id, "title": new_plan.title, "description": new_plan.description, "renewal_period": new_plan.renewal_period}

@router.get("/{id}")
def get_plan(id: int, db: Session = Depends(get_db)):
    plan = db.query(Plan).filter(Plan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{plan_id}")
def update_plan(plan_id: int, plan: PlanUpdate, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for key, value in plan.model_dump(exclude_unset=True).items():
        setattr(db_plan, key, value)
    db.commit()
    return {"message": "Plan updated successfully", "title": db_plan.title, "description": db_plan.description, "renewal_period": db_plan.renewal_period}

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(db_plan)
    db.commit()
    return {"message": "Plan deleted successfully"}
