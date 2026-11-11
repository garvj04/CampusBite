from pydantic import BaseModel


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str = "DUMMY"


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    status: str
    transaction_id: str

    class Config:
        from_attributes = True
