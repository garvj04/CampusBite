from fastapi import FastAPI
from app.database.connection import Base, engine

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem

from app.routers.course import router as course_router
from app.routers.enrollment import router as enrollment_router
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.restaurant import router as restaurant_router
from app.routers.menu_item import router as menu_item_router


app = FastAPI(title="CampusBite API")


Base.metadata.create_all(bind=engine)


app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(restaurant_router)
app.include_router(menu_item_router)


@app.get("/")
def root():
    return {"message": "CampusBite API is running"}