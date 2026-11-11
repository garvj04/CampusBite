from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database.connection import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    restaurant_id = Column(
        Integer,
        ForeignKey("restaurants.id"),
        nullable=False
    )