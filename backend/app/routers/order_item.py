from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.menu_item import MenuItem
from app.schemas.order_item import (
    OrderItemCreate,
    OrderItemResponse
)


router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


@router.post("/", response_model=OrderItemResponse)
def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == item.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    menu_item = db.query(MenuItem).filter(
        MenuItem.id == item.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    new_order_item = OrderItem(
        order_id=item.order_id,
        menu_item_id=item.menu_item_id,
        quantity=item.quantity,
        price=item.price
    )

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    return new_order_item


@router.get("/", response_model=list[OrderItemResponse])
def get_order_items(
    db: Session = Depends(get_db)
):
    return db.query(OrderItem).all()


@router.get(
    "/order/{order_id}",
    response_model=list[OrderItemResponse]
)
def get_order_items_for_order(
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

    return db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()


@router.get(
    "/{order_item_id}",
    response_model=OrderItemResponse
)
def get_order_item(
    order_item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Order item not found"
        )

    return item