from pydantic import BaseModel
from datetime import date

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