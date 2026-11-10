from pydantic import BaseModel


class CourseCreate(BaseModel):
    name: str
    description: str


class CourseResponse(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True
