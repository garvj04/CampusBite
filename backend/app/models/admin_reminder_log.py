from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.connection import Base


class AdminReminderLog(Base):
    __tablename__ = "admin_reminder_logs"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=True
    )

    message = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )
