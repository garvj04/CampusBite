from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="CUSTOMER")

    restaurants = relationship("Restaurant", back_populates="owner", foreign_keys="Restaurant.owner_id")
    customer_orders = relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    delivery_orders = relationship("Order", back_populates="delivery_partner", foreign_keys="Order.delivery_partner_id")
    reviews = relationship("Review", back_populates="customer")
