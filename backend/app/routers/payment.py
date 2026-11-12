from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.payment import PaymentLedger
from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("/", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if current_user.role != "CUSTOMER" or order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    item_count = db.query(OrderItem).filter(
        OrderItem.order_id == order.id
    ).count()

    if item_count == 0 or order.total_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot pay for an empty order"
        )

    existing_payment = db.query(PaymentLedger).filter(
        PaymentLedger.order_id == payment.order_id
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists for this order"
        )

    new_payment = PaymentLedger(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment.payment_method,
        status="PAID",
        transaction_id=f"DUMMY-{uuid4().hex[:12].upper()}"
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


@router.get(
    "/",
    response_model=list[PaymentResponse]
)
def get_payments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if current_user.role == "ADMIN":
        return db.query(PaymentLedger).all()

    if current_user.role == "CUSTOMER":
        return db.query(PaymentLedger).join(Order).filter(
            Order.customer_id == current_user.id
        ).all()

    raise HTTPException(status_code=403, detail="Access denied")


@router.get(
    "/order/{order_id}",
    response_model=PaymentResponse
)
def get_payment_for_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    payment = db.query(PaymentLedger).filter(
        PaymentLedger.order_id == order_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found for this order"
        )

    order = db.query(Order).filter(Order.id == order_id).first()
    if current_user.role != "ADMIN" and not (
        current_user.role == "CUSTOMER"
        and order.customer_id == current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return payment


@router.patch(
    "/{payment_id}/refund",
    response_model=PaymentResponse
)
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    payment = db.query(PaymentLedger).filter(
        PaymentLedger.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can issue refunds")

    if payment.status != "PAID":
        raise HTTPException(
            status_code=400,
            detail="Only PAID payments can be refunded"
        )

    order = db.query(Order).filter(
        Order.id == payment.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found for this payment"
        )

    if order.status not in ("DELIVERED", "CANCELLED"):
        raise HTTPException(
            status_code=400,
            detail="Only delivered or cancelled orders can be refunded"
        )

    payment.status = "REFUNDED"
    order.status = "REFUNDED"

    db.commit()
    db.refresh(payment)

    return payment
