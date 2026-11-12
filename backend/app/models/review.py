from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base


class Review(Base):
    __tablename__ = "reviews"

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

    rating = Column(Integer, nullable=False)

    comment = Column(String, nullable=True)
    customer = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
