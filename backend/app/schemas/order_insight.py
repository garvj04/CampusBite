from pydantic import BaseModel


class OrderInsightResponse(BaseModel):
    insight: str
