from pydantic import BaseModel
from typing import Optional

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