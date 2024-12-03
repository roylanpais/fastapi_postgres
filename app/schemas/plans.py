from pydantic import BaseModel, Field

class PlanBase(BaseModel):
    title: str
    description: str
    renewal_period: int = Field(..., gt=0, description="Renewal period must be greater than 0")

class PlanCreate(PlanBase):
    pass

class PlanUpdate(PlanBase):
    pass
