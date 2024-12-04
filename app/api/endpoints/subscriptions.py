from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.db.models import User, Subscription
from app.schemas.subscriptions import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from app.utils import get_current_user

router = APIRouter()

# Subscription endpoints
@router.get("/")
def get_subscriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Subscription).all()

@router.post("/")
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_subscription = Subscription(**subscription.model_dump())
    db.add(new_subscription)
    db.commit()
    return {"message": "Subscription created successfully", "id": new_subscription.id, "price": new_subscription.price}

@router.get("/{id}")
def get_subscription(id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.put("/{subscription_id}")
def update_subscription(subscription_id: int, subscription: SubscriptionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for key, value in subscription.model_dump(exclude_unset=True).items():
        setattr(db_subscription, key, value)
    db.commit()
    return {"message": "Subscription updated successfully", "price": db_subscription.price}

@router.delete("/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.is_active = False
    db.commit()
    return {"message": "Subscription deleted successfully"}