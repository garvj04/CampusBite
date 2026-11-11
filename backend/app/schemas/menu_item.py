from pydantic import BaseModel


class MenuItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    restaurant_id: int


class MenuItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    restaurant_id: int

    class Config:
        from_attributes = True