from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.course import Course
from app.schemas.course import CourseCreate, CourseResponse


router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(
        name=course.name,
        description=course.description
    )

    db.add(new_course)
    db.commit()
    db.refresh(new_course)

    return new_course


@router.get("/", response_model=list[CourseResponse])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return courses
