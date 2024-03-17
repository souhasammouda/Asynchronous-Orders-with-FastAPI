from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Status(str, Enum):
    active = 'Active'
    deleted = 'Inactive'

class ProductIn(BaseModel):
    name: str
    price_net: int
    quantity: int
    status: Status

class ProductOut(ProductIn):
    product_id: int

class OrderDetails(BaseModel):
    order_id: int
    product_id: int
    quantity: int

class ProductUpdate(ProductIn):
    name: Optional[str] = None
    customer_class: Optional[str] = None
    price_net: Optional[int] = None
    status: Optional[Status] = None

class DevisIn(BaseModel):
    id: int

class Order(BaseModel):
    order_id: int
    customer_id: int
    product_id: int
    quantity: int
    price_net: int
    status: str

class Devis(BaseModel):
    order_id: int
    status: str

class DevisValidation(BaseModel):
    order_id: int
    isValid: bool