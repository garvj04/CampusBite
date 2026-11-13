from pydantic import BaseModel


class RestaurantCreate(BaseModel):
    name: str
    description: str | None = None
    address: str


class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    address: str
    owner_id: int

    class Config:
        from_attributes = True