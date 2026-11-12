from fastapi import APIRouter, Depends, HTTPException, Query
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


def check_order_access(order, current_user, db, allow_unassigned_delivery=False):
    if current_user.role == "ADMIN":
        return

    if current_user.role == "CUSTOMER" and order.customer_id == current_user.id:
        return

    if current_user.role == "RESTAURANT_OWNER":
        owned = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id,
            Restaurant.owner_id == current_user.id
        ).first()
        if owned:
            return

    if current_user.role == "DELIVERY_PARTNER":
        if order.delivery_partner_id == current_user.id:
            return
        if allow_unassigned_delivery and order.status == "READY" and order.delivery_partner_id is None:
            return

    raise HTTPException(status_code=403, detail="Access denied")


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "CUSTOMER" or order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Customers can only create their own orders")

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
        total_amount=0.0,
        status="PLACED"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


@router.get("/", response_model=list[OrderResponse])
def get_orders(
    status: str | None = Query(default=None),
    restaurant_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Order)

    if current_user.role == "CUSTOMER":
        query = query.filter(Order.customer_id == current_user.id)
    elif current_user.role == "RESTAURANT_OWNER":
        query = query.join(Restaurant).filter(Restaurant.owner_id == current_user.id)
    elif current_user.role == "DELIVERY_PARTNER":
        query = query.filter(
            (Order.delivery_partner_id == current_user.id) |
            ((Order.status == "READY") & (Order.delivery_partner_id.is_(None)))
        )
    elif current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    if status:
        normalized_status = status.upper()
        if normalized_status not in ALLOWED_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid order status filter")
        query = query.filter(Order.status == normalized_status)

    if restaurant_id is not None:
        query = query.filter(Order.restaurant_id == restaurant_id)

    return query.order_by(Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    check_order_access(order, current_user, db)
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

    if current_user.role == "ADMIN":
        pass

    elif current_user.role == "RESTAURANT_OWNER":
        owned = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id,
            Restaurant.owner_id == current_user.id
        ).first()

        if not owned or status_update.status not in {
            "ACCEPTED", "PREPARING", "READY", "CANCELLED"
        }:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "DELIVERY_PARTNER":
        if (
            order.delivery_partner_id != current_user.id
            or status_update.status not in {
                "OUT_FOR_DELIVERY", "DELIVERED"
            }
        ):
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "CUSTOMER":
        if (
            order.customer_id != current_user.id
            or status_update.status != "CANCELLED"
            or order.status != "PLACED"
        ):
            raise HTTPException(status_code=403, detail="Access denied")

    else:
        raise HTTPException(status_code=403, detail="Access denied")

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

    if current_user.role == "RESTAURANT_OWNER":
        owned = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id,
            Restaurant.owner_id == current_user.id
        ).first()
        if not owned:
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role == "DELIVERY_PARTNER":
        if (
            assignment.delivery_partner_id != current_user.id
            or order.delivery_partner_id is not None
        ):
            raise HTTPException(status_code=403, detail="Access denied")

    elif current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

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