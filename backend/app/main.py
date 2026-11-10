from fastapi import FastAPI
from app.database.connection import Base, engine

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment

from app.routers.course import router as course_router
from app.routers.enrollment import router as enrollment_router


app = FastAPI(title="CampusBite API")


Base.metadata.create_all(bind=engine)


app.include_router(course_router)
app.include_router(enrollment_router)


@app.get("/")
def root():
    return {"message": "CampusBite API is running"}
