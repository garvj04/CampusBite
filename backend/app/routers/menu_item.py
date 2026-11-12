from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.menu_item import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse


router = APIRouter(
    prefix="/menu-items",
    tags=["Menu Items"]
)


@router.post("/", response_model=MenuItemResponse)
def create_menu_item(
    item: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    restaurant = db.query(Restaurant).filter(
        Restaurant.id == item.restaurant_id
    ).first()

    if not restaurant:
        raise HTTPException(
            status_code=404,
            detail="Restaurant not found"
        )

    if current_user.role != "ADMIN" and not (
        current_user.role == "RESTAURANT_OWNER"
        and restaurant.owner_id == current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    new_item = MenuItem(
        name=item.name,
        description=item.description,
        price=item.price,
        restaurant_id=item.restaurant_id
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/", response_model=list[MenuItemResponse])
def get_menu_items(
    db: Session = Depends(get_db)
):
    return db.query(MenuItem).all()


@router.get(
    "/restaurant/{restaurant_id}",
    response_model=list[MenuItemResponse]
)
def get_restaurant_menu_items(
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

    return db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id
    ).all()


@router.get(
    "/{menu_item_id}",
    response_model=MenuItemResponse
)
def get_menu_item(
    menu_item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(MenuItem).filter(
        MenuItem.id == menu_item_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Menu item not found"
        )

    return item