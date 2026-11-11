from pydantic import BaseModel


class AdminReminderLogCreate(BaseModel):
    order_id: int | None = None
    message: str
    status: str = "PENDING"


class AdminReminderLogResponse(BaseModel):
    id: int
    order_id: int | None = None
    message: str
    status: str

    class Config:
        from_attributes = True
