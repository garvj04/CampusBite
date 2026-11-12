from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.admin_reminder_log import AdminReminderLog
from app.models.order import Order
from app.schemas.admin_reminder_log import (
    AdminReminderLogCreate,
    AdminReminderLogResponse
)
from app.core.dependencies import require_role


router = APIRouter(
    prefix="/admin-reminder-logs",
    tags=["Admin Reminder Logs"]
)


@router.post(
    "/",
    response_model=AdminReminderLogResponse
)
def create_reminder_log(
    reminder: AdminReminderLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ADMIN"))
):
    if reminder.order_id is not None:
        order = db.query(Order).filter(
            Order.id == reminder.order_id
        ).first()

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

    new_reminder = AdminReminderLog(
        order_id=reminder.order_id,
        message=reminder.message,
        status=reminder.status
    )

    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)

    return new_reminder


@router.get(
    "/",
    response_model=list[AdminReminderLogResponse]
)
def get_reminder_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ADMIN"))
):
    return db.query(AdminReminderLog).all()


@router.get(
    "/{reminder_id}",
    response_model=AdminReminderLogResponse
)
def get_reminder_log(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ADMIN"))
):
    reminder = db.query(AdminReminderLog).filter(
        AdminReminderLog.id == reminder_id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=404,
            detail="Reminder log not found"
        )

    return reminder
