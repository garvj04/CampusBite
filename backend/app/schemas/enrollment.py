from pydantic import BaseModel


class EnrollmentCreate(BaseModel):
    user_id: int
    course_id: int


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int

    class Config:
        from_attributes = True
