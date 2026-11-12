from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.review import Review
from app.models.order import Order
from app.models.user import User
from app.models.restaurant import Restaurant
from app.schemas.review import ReviewCreate, ReviewResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "CUSTOMER" or review.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Customers can only submit their own reviews")

    delivered_order = db.query(Order).filter(
        Order.customer_id == current_user.id,
        Order.restaurant_id == review.restaurant_id,
        Order.status == "DELIVERED"
    ).first()

    if not delivered_order:
        raise HTTPException(
            status_code=400,
            detail="You can review a restaurant only after a delivered order"
        )

    existing_review = db.query(Review).filter(
        Review.customer_id == current_user.id,
        Review.restaurant_id == review.restaurant_id
    ).first()

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="You have already reviewed this restaurant"
        )

    if review.rating < 1 or review.rating > 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5"
        )

    customer = db.query(User).filter(
        User.id == review.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == review.restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    new_review = Review(
        customer_id=review.customer_id,
        restaurant_id=review.restaurant_id,
        rating=review.rating,
        comment=review.comment
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return new_review


@router.get("/", response_model=list[ReviewResponse])
def get_reviews(
    db: Session = Depends(get_db)
):
    return db.query(Review).all()


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[ReviewResponse]
)
def get_restaurant_reviews(
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

    return db.query(Review).filter(
        Review.restaurant_id == restaurant_id
    ).all()


@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    review = db.query(Review).filter(
        Review.id == review_id
    ).first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    return review
