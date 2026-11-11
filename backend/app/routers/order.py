from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.order import Order
from app.models.user import User
from app.models.restaurant import Restaurant
from app.schemas.order import (
    OrderCreate,
    OrderStatusUpdate,
    DeliveryPartnerAssignment,
    OrderResponse
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


ALLOWED_STATUSES = {
    "PLACED",
    "ACCEPTED",
    "PREPARING",
    "READY",
    "ASSIGNED",
    "OUT_FOR_DELIVERY",
    "DELIVERED",
    "CANCELLED",
    "REFUNDED"
}


VALID_TRANSITIONS = {
    "PLACED": {"ACCEPTED", "CANCELLED"},
    "ACCEPTED": {"PREPARING", "CANCELLED"},
    "PREPARING": {"READY", "CANCELLED"},
    "READY": {"ASSIGNED", "CANCELLED"},
    "ASSIGNED": {"OUT_FOR_DELIVERY"},
    "OUT_FOR_DELIVERY": {"DELIVERED"},
    "DELIVERED": {"REFUNDED"},
    "CANCELLED": {"REFUNDED"},
    "REFUNDED": set()
}


@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(User).filter(
        User.id == order.customer_id
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == order.restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    new_order = Order(
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id,
        total_amount=order.total_amount,
        status="PLACED"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db)
):
    return db.query(Order).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if status_update.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    if status_update.status not in VALID_TRANSITIONS[order.status]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change order status from "
                f"{order.status} to {status_update.status}"
            )
        )

    order.status = status_update.status

    db.commit()
    db.refresh(order)

    return order


@router.patch(
    "/{order_id}/assign-delivery",
    response_model=OrderResponse
)
def assign_delivery_partner(
    order_id: int,
    assignment: DeliveryPartnerAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    delivery_partner = db.query(User).filter(
        User.id == assignment.delivery_partner_id
    ).first()

    if not delivery_partner:
        raise HTTPException(
            status_code=404,
            detail="Delivery partner not found"
        )

    if delivery_partner.role != "DELIVERY_PARTNER":
        raise HTTPException(
            status_code=400,
            detail="Selected user is not a delivery partner"
        )

    if order.status != "READY":
        raise HTTPException(
            status_code=400,
            detail="Order must be READY before assigning a delivery partner"
        )

    order.delivery_partner_id = delivery_partner.id
    order.status = "ASSIGNED"

    db.commit()
    db.refresh(order)

    return order