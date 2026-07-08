from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Review, BorrowRecord, Book
from app.schema import ReviewCreate
from app.utils import get_current_user

router = APIRouter(prefix="/reviews", tags=["Review"])


@router.post("")
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Check whether the book exists
    book = (
        db.query(Book)
        .filter(Book.id == review_data.book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )

    # Check whether the user has borrowed the book
    borrowed = (
    db.query(BorrowRecord)
    .filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == review_data.book_id,
        BorrowRecord.return_date.isnot(None))
    .first()
    )

    if not borrowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review books that you have borrowed."
        )

    # Check if the user already reviewed the book
    existing_review = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.book_id == review_data.book_id,
        )
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this book."
        )

    review = Review(
        rating=review_data.rating,
        review=review_data.review,
        user_id=current_user.id,
        book_id=review_data.book_id,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "message": "Review added successfully.",
        "review": review,
    }

@router.get("/{book_id}")
def get_book_reviews(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    reviews = (
        db.query(Review)
        .filter(Review.book_id == book_id)
        .all()
    )

    if not reviews:
        return {
            "message": "No reviews available for this book."
        }

    return {
        "reviews": reviews
    }

@router.put("/{review_id}")
def update_review(
    review_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review_query = (
        db.query(Review)
        .filter(Review.id == review_id)
    )

    review = review_query.first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found."
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized."
        )

    review_query.update(
        review_data.model_dump(),
        synchronize_session=False,
    )

    db.commit()

    return {
        "message": "Review updated successfully.",
        "review": review_query.first(),
    }

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    review_query = (
        db.query(Review)
        .filter(Review.id == review_id)
    )

    review = review_query.first()

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Review not found."
        )

    if (
        review.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="You are not authorized."
        )

    review_query.delete(synchronize_session=False)

    db.commit()

    return {
        "message": "Review deleted successfully."
    }