from fastapi import FastAPI
from app.database.connection import Base, engine

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment

app = FastAPI(title="CampusBite API")


Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "CampusBite API is running"}
