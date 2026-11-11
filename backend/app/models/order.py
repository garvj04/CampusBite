from sqlalchemy import Column, Integer, Float, String, ForeignKey
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

    total_amount = Column(Float, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="PLACED"
    )