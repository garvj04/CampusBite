import asyncio

from fastapi import FastAPI
from app.database.connection import Base, engine, SessionLocal

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.restaurant import Restaurant
from app.models.menu_item import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.payment import PaymentLedger
from app.models.admin_reminder_log import AdminReminderLog

from app.routers.course import router as course_router
from app.routers.enrollment import router as enrollment_router
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.restaurant import router as restaurant_router
from app.routers.menu_item import router as menu_item_router
from app.routers.order import router as order_router
from app.routers.order_item import router as order_item_router
from app.routers.review import router as review_router
from app.routers.payment import router as payment_router
from app.routers.admin_reminder_log import router as admin_reminder_log_router
from app.tasks.order_reminders import check_stale_orders


app = FastAPI(title="CampusBite API")


async def stale_order_reminder_loop():
    while True:
        db = SessionLocal()

        try:
            check_stale_orders(db)
        finally:
            db.close()

        await asyncio.sleep(60)


@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(stale_order_reminder_loop())


Base.metadata.create_all(bind=engine)


app.include_router(course_router)
app.include_router(enrollment_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(restaurant_router)
app.include_router(menu_item_router)
app.include_router(order_router)
app.include_router(order_item_router)
app.include_router(review_router)
app.include_router(payment_router)
app.include_router(admin_reminder_log_router)


@app.get("/")
def root():
    return {"message": "CampusBite API is running"}