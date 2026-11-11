from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.admin_reminder_log import AdminReminderLog


def check_stale_orders(db: Session):
    stale_orders = db.query(Order).filter(
        Order.status == "PLACED"
    ).all()

    for order in stale_orders:
        existing_reminder = db.query(AdminReminderLog).filter(
            AdminReminderLog.order_id == order.id,
            AdminReminderLog.status == "PENDING"
        ).first()

        if existing_reminder:
            continue

        reminder = AdminReminderLog(
            order_id=order.id,
            message=f"Order #{order.id} has been waiting in PLACED status",
            status="PENDING"
        )

        db.add(reminder)

    db.commit()
