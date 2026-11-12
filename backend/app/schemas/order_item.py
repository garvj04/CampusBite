from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    order_id: int
    menu_item_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_item_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True