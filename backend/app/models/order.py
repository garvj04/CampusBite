from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )

    delivery_partner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    total_amount = Column(Float, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="PLACED"
    )

    customer = relationship("User", back_populates="customer_orders", foreign_keys=[customer_id])
    delivery_partner = relationship("User", back_populates="delivery_orders", foreign_keys=[delivery_partner_id])
    restaurant = relationship("Restaurant", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("PaymentLedger", back_populates="order")
    reminder_logs = relationship("AdminReminderLog", back_populates="order")
