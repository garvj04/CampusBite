from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.restaurant import Restaurant
from app.models.user import User
from app.models.order import Order
from app.models.review import Review
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantResponse
)


router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"]
)


@router.post("/", response_model=RestaurantResponse)
def create_restaurant(
    restaurant: RestaurantCreate,
    db: Session = Depends(get_db)
):
    owner = db.query(User).filter(
        User.id == restaurant.owner_id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=404,
            detail="Restaurant owner not found"
        )

    new_restaurant = Restaurant(
        name=restaurant.name,
        description=restaurant.description,
        address=restaurant.address,
        owner_id=restaurant.owner_id
    )

    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    return new_restaurant


@router.get("/", response_model=list[RestaurantResponse])
def get_restaurants(
    db: Session = Depends(get_db)
):
    return db.query(Restaurant).all()


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    return restaurant

@router.get("/{restaurant_id}/statistics")
def get_restaurant_statistics(
    restaurant_id: int,
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    orders = db.query(Order).filter(
        Order.restaurant_id == restaurant_id
    ).all()

    reviews = db.query(Review).filter(
        Review.restaurant_id == restaurant_id
    ).all()

    total_orders = len(orders)
    delivered_orders = sum(
        1 for order in orders
        if order.status == "DELIVERED"
    )
    cancelled_orders = sum(
        1 for order in orders
        if order.status == "CANCELLED"
    )
    refunded_orders = sum(
        1 for order in orders
        if order.status == "REFUNDED"
    )

    total_revenue = sum(
        order.total_amount
        for order in orders
        if order.status == "DELIVERED"
    )

    review_count = len(reviews)

    average_rating = (
        sum(review.rating for review in reviews) / review_count
        if review_count > 0
        else 0
    )

    return {
        "restaurant_id": restaurant.id,
        "restaurant_name": restaurant.name,
        "total_orders": total_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "refunded_orders": refunded_orders,
        "total_revenue": total_revenue,
        "review_count": review_count,
        "average_rating": average_rating
    }
