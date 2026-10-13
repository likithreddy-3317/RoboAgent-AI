from typing import Literal
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    product: str = Field(description="Product name")
    quantity: int = Field(gt=0)

class WarehouseOrder(BaseModel):
    order_id: str = "ORDER-1001"
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    items: list[OrderItem] = Field(min_length=1)
    delivery_station: str = "PACKING"
