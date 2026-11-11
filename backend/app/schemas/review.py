from pydantic import BaseModel


class ReviewCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    rating: int
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    rating: int
    comment: str | None = None

    class Config:
        from_attributes = True
