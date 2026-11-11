from pydantic import BaseModel


class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    total_amount: float


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    total_amount: float
    status: str

    class Config:
        from_attributes = True