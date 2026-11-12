from pydantic import BaseModel


class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int


class OrderStatusUpdate(BaseModel):
    status: str


class DeliveryPartnerAssignment(BaseModel):
    delivery_partner_id: int


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    delivery_partner_id: int | None = None
    total_amount: float
    status: str

    class Config:
        from_attributes = True