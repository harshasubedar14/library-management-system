from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Author, Category, Publisher
from app.schema import BookCreate,BookUpdate
from app.utils import get_current_user

router = APIRouter(prefix="/books", tags=["Book"])


@router.post("")
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Only Admin can create books
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to create books."
        )

    # ISBN must be unique
    book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
    if book:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ISBN '{book_data.isbn}' already exists."
        )

    # Validate Author
    author = db.query(Author).filter(
        Author.id == book_data.author_id
    ).first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found."
        )

    # Validate Category
    category = db.query(Category).filter(
        Category.id == book_data.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    # Validate Publisher
    publisher = db.query(Publisher).filter(
        Publisher.id == book_data.publisher_id
    ).first()

    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found."
        )

    # Validate Copies
    if book_data.available_copies > book_data.total_copies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Available copies cannot be greater than total copies."
        )

    new_book = Book(**book_data.model_dump())

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return {
        "message": "Book created successfully.",
        "book": new_book
    }

@router.get("")
def get_books(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    books = db.query(Book).all()

    if not books:
        return {"message": "No books found."}

    return {
        "books": books
    }

@router.get("/{book_id}")
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )

    return {
        "book": book
    }

@router.put("/{book_id}")
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to update books."
        )

    book_query = db.query(Book).filter(Book.id == book_id)
    book = book_query.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )

    update_data = book_data.model_dump(exclude_unset=True)

    # Validate ISBN
    if "isbn" in update_data:
        duplicate = (
            db.query(Book)
            .filter(
                Book.isbn == update_data["isbn"],
                Book.id != book_id,
            )
            .first()
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="ISBN already exists."
            )

    # Validate foreign keys if updated
    if "author_id" in update_data:
        if not db.query(Author).filter(
            Author.id == update_data["author_id"]
        ).first():
            raise HTTPException(
                status_code=404,
                detail="Author not found."
            )

    if "category_id" in update_data:
        if not db.query(Category).filter(
            Category.id == update_data["category_id"]
        ).first():
            raise HTTPException(
                status_code=404,
                detail="Category not found."
            )

    if "publisher_id" in update_data:
        if not db.query(Publisher).filter(
            Publisher.id == update_data["publisher_id"]
        ).first():
            raise HTTPException(
                status_code=404,
                detail="Publisher not found."
            )

    # Validate copies
    total = update_data.get(
        "total_copies",
        book.total_copies,
    )

    available = update_data.get(
        "available_copies",
        book.available_copies,
    )

    if available > total:
        raise HTTPException(
            status_code=400,
            detail="Available copies cannot exceed total copies."
        )

    book_query.update(
        update_data,
        synchronize_session=False,
    )

    db.commit()

    return {
        "message": "Book updated successfully.",
        "book": book_query.first()
    }

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to delete books."
        )

    book_query = db.query(Book).filter(Book.id == book_id)

    book = book_query.first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found."
        )

    book_query.delete(synchronize_session=False)

    db.commit()

    return {
        "message": "Book deleted successfully."
    }