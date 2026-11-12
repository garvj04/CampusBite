from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.order_item import OrderItem
from app.models.order import Order
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.order_item import OrderItemCreate, OrderItemResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)


def check_order_item_access(order, current_user, db):
    if current_user.role == "ADMIN":
        return

    if current_user.role == "CUSTOMER" and order.customer_id == current_user.id:
        return

    if current_user.role == "RESTAURANT_OWNER":
        restaurant = db.query(Restaurant).filter(
            Restaurant.id == order.restaurant_id,
            Restaurant.owner_id == current_user.id
        ).first()
        if restaurant:
            return

    if (
        current_user.role == "DELIVERY_PARTNER"
        and order.delivery_partner_id == current_user.id
    ):
        return

    raise HTTPException(status_code=403, detail="Access denied")


@router.post("/", response_model=OrderItemResponse)
def create_order_item(
    item: OrderItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == item.order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if (
        current_user.role != "CUSTOMER"
        or order.customer_id != current_user.id
        or order.status != "PLACED"
    ):
        raise HTTPException(status_code=403, detail="Cannot add items to this order")

    menu_item = db.query(MenuItem).filter(
        MenuItem.id == item.menu_item_id
    ).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    if menu_item.restaurant_id != order.restaurant_id:
        raise HTTPException(
            status_code=400,
            detail="Menu item does not belong to this restaurant"
        )

    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    new_order_item = OrderItem(
        order_id=item.order_id,
        menu_item_id=item.menu_item_id,
        quantity=item.quantity,
        price=menu_item.price
    )

    db.add(new_order_item)
    db.commit()
    db.refresh(new_order_item)

    return new_order_item


@router.get("/", response_model=list[OrderItemResponse])
def get_order_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(OrderItem).join(Order)

    if current_user.role == "CUSTOMER":
        query = query.filter(Order.customer_id == current_user.id)

    elif current_user.role == "RESTAURANT_OWNER":
        query = query.join(Restaurant).filter(
            Restaurant.owner_id == current_user.id
        )

    elif current_user.role == "DELIVERY_PARTNER":
        query = query.filter(
            Order.delivery_partner_id == current_user.id
        )

    elif current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")

    return query.all()


@router.get(
    "/order/{order_id}",
    response_model=list[OrderItemResponse]
)
def get_order_items_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    check_order_item_access(order, current_user, db)

    return db.query(OrderItem).filter(
        OrderItem.order_id == order_id
    ).all()


@router.get(
    "/{order_item_id}",
    response_model=OrderItemResponse
)
def get_order_item(
    order_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(OrderItem).filter(
        OrderItem.id == order_item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    order = db.query(Order).filter(
        Order.id == item.order_id
    ).first()

    check_order_item_access(order, current_user, db)

    return item
