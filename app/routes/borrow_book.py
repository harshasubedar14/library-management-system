from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import Book, BorrowRecord
from app.schema import BorrowBook
from app.utils import get_current_user

router = APIRouter(prefix="/borrow", tags=["Borrow"])


@router.post("")
def borrow_book(
    borrow_data: BorrowBook,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # Check book
    book = db.query(Book).filter(Book.id == borrow_data.book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )

    # Check availability
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available."
        )

    # Check if already borrowed
    already_borrowed = (
        db.query(BorrowRecord)
        .filter(
            BorrowRecord.user_id == current_user.id,
            BorrowRecord.book_id == borrow_data.book_id,
            BorrowRecord.return_date == None
        )
        .first()
    )

    if already_borrowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already borrowed this book."
        )

    # Create borrow record
    borrow_record = BorrowRecord(
        user_id=current_user.id,
        book_id=borrow_data.book_id,
        borrow_date=date.today(),
        due_date=borrow_data.due_date,
        status="Borrowed"
    )

    # Reduce available copies
    book.available_copies -= 1

    db.add(borrow_record)
    db.commit()
    db.refresh(borrow_record)

    return {
        "message": "Book borrowed successfully.",
        "borrow_record": borrow_record
    }


@router.patch("/{borrow_id}/return")
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    borrow_record = (
        db.query(BorrowRecord)
        .filter(BorrowRecord.id == borrow_id)
        .first()
    )

    if not borrow_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found."
        )

    # Borrower or Admin
    if (
        borrow_record.user_id != current_user.id
        and current_user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to return this book."
        )

    # Already returned
    if borrow_record.return_date is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has already been returned."
        )

    # Update borrow record
    borrow_record.return_date = date.today()
    borrow_record.status = "Returned"

    # Increase available copies
    if borrow_record.book.available_copies < borrow_record.book.total_copies:
        borrow_record.book.available_copies += 1

    db.commit()
    db.refresh(borrow_record)

    return {
        "message": "Book returned successfully.",
        "borrow_record": borrow_record
    }   