from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.order import Order
from app.models.user import User
from app.schemas.order_insight import OrderInsightResponse
from app.services.openai_service import generate_order_insight


router = APIRouter(
    prefix="/order-insight",
    tags=["Order Insight"]
)


@router.get(
    "/",
    response_model=OrderInsightResponse
)
def get_order_insight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.customer_id == current_user.id
    ).all()

    if not orders:
        raise HTTPException(
            status_code=404,
            detail="No order history found for this customer"
        )

    order_history = [
        {
            "order_id": order.id,
            "restaurant_id": order.restaurant_id,
            "total_amount": order.total_amount,
            "status": order.status
        }
        for order in orders
    ]

    insight = generate_order_insight(order_history)

    return OrderInsightResponse(
        insight=insight
    )
