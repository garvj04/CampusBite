from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class PaymentLedger(Base):
    __tablename__ = "payment_ledger"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    payment_method = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False,
        default="PENDING"
    )

    transaction_id = Column(
        String,
        nullable=False,
        unique=True
    )
    order = relationship("Order", back_populates="payments")
