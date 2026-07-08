from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.schema import CategoryCreate, CategoryUpdate
from app.utils import get_current_user

router = APIRouter(prefix="/categories", tags=["Category"])


@router.post("")
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to create categories.",
        )

    category_exist = (
        db.query(Category)
        .filter(Category.name == category_data.name)
        .first()
    )

    if category_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_data.name}' already exists.",
        )

    category = Category(**category_data.dict())

    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "message": "Category created successfully.",
        "category": category,
    }


@router.get("")
def get_categories(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    categories = db.query(Category).all()

    if not categories:
        return {"message": "No categories found."}

    return {"categories": categories}


@router.get("/{category_id}")
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    return {"category": category}


@router.put("/{category_id}")
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to update categories.",
        )

    category_query = (
        db.query(Category)
        .filter(Category.id == category_id)
    )

    category = category_query.first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    duplicate = (
        db.query(Category)
        .filter(
            Category.name == category_data.name,
            Category.id != category_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_data.name}' already exists.",
        )

    category_query.update(
        category_data.dict(),
        synchronize_session=False,
    )

    db.commit()

    return {
        "message": "Category updated successfully.",
        "category": category_query.first(),
    }


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to delete categories.",
        )

    category_query = (
        db.query(Category)
        .filter(Category.id == category_id)
    )

    category = category_query.first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        )

    category_query.delete(synchronize_session=False)
    db.commit()

    return {"message": "Category deleted successfully."}