from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Publisher, Book
from app.schema import PublisherCreate, PublisherUpdate
from app.utils import get_current_user

router = APIRouter(prefix="/publishers", tags=["Publisher"])


@router.post("")
def create_publisher(
    publisher_data: PublisherCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to create publishers."
        )

    publisher_exists = (
        db.query(Publisher)
        .filter(Publisher.name == publisher_data.name)
        .first()
    )

    if publisher_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Publisher '{publisher_data.name}' already exists."
        )

    publisher = Publisher(**publisher_data.dict())

    db.add(publisher)
    db.commit()
    db.refresh(publisher)

    return {
        "message": "Publisher created successfully.",
        "publisher": publisher,
    }


@router.get("")
def get_publishers(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    publishers = db.query(Publisher).all()

    if not publishers:
        return {"message": "No publishers found."}

    return {"publishers": publishers}


@router.get("/{publisher_id}")
def get_publisher(
    publisher_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    publisher = (
        db.query(Publisher)
        .filter(Publisher.id == publisher_id)
        .first()
    )

    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found."
        )

    return {"publisher": publisher}


@router.put("/{publisher_id}")
def update_publisher(
    publisher_id: int,
    publisher_data: PublisherUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to update publishers."
        )

    publisher_query = (
        db.query(Publisher)
        .filter(Publisher.id == publisher_id)
    )

    publisher = publisher_query.first()

    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found."
        )

    duplicate = (
        db.query(Publisher)
        .filter(
            Publisher.name == publisher_data.name,
            Publisher.id != publisher_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Publisher '{publisher_data.name}' already exists."
        )

    publisher_query.update(
        publisher_data.dict(),
        synchronize_session=False,
    )

    db.commit()

    return {
        "message": "Publisher updated successfully.",
        "publisher": publisher_query.first(),
    }


@router.delete("/{publisher_id}")
def delete_publisher(
    publisher_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to delete publishers."
        )

    publisher_query = (
        db.query(Publisher)
        .filter(Publisher.id == publisher_id)
    )

    publisher = publisher_query.first()

    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found."
        )

    book = (
        db.query(Book)
        .filter(Book.publisher_id == publisher_id)
        .first()
    )

    if book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete publisher because books are associated with it."
        )

    publisher_query.delete(synchronize_session=False)
    db.commit()

    return {
        "message": "Publisher deleted successfully."
    }