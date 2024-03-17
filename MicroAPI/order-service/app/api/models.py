from pydantic import BaseModel
from typing import Optional

class OrderIn(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    price_net: int
    status: str = "pending"

class OrderOut(OrderIn):
    order_id: int

class OrderUpdate(OrderIn):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    price_net: Optional[int] = None

class DevisIn(BaseModel):
    id: int

class ValidateDevis(BaseModel):
    order_id: int
    isValid: bool
