from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Author, Book
from app.schema import AuthorCreate
from app.utils import get_current_user

router = APIRouter(prefix="/authors",tags=['Author'])

@router.post("")
def create_author(author_data:AuthorCreate,db:Session = Depends(get_db),current_user = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Only admins are authorized to create author")
    
    author_exist = db.query(Author).filter(Author.name == author_data.name)
    if author_exist.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f"Author '{author_data.name}' already exists.")
    author = Author(**author_data.dict())
    db.add(author)
    db.commit()
    db.refresh(author)
    return {"message":"Author created","author":author}

@router.get("")
def get_authors(db:Session = Depends(get_db),current_user = Depends(get_current_user)):
    authors = db.query(Author).all()
    if not authors:
        return {"message":"No authors exists"}
    return {"authors":authors}

@router.get("/{author_id}")
def get_authors(author_id : int,db:Session = Depends(get_db),current_user = Depends(get_current_user)):
    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        return {"message":"No authors exists"}
    return {"author":author}

@router.put("/{author_id}")
def update_author(
    author_id: int,
    author_data: AuthorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to update authors."
        )

    author_query = db.query(Author).filter(Author.id == author_id)
    author = author_query.first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found."
        )

    # Check if another author already has the same name
    existing_author = (
        db.query(Author)
        .filter(
            Author.name == author_data.name,
            Author.id != author_id
        )
        .first()
    )

    if existing_author:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Author '{author_data.name}' already exists."
        )

    author_query.update(
        author_data.dict(),
        synchronize_session=False
    )

    db.commit()

    return {
        "message": "Author updated successfully.",
        "author": author_query.first()
    }

@router.delete("/{author_id}")
def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins are authorized to delete authors."
        )

    author_query = db.query(Author).filter(Author.id == author_id)
    author = author_query.first()

    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found."
        )

    # Prevent deletion if books exist for this author
    book = db.query(Book).filter(Book.author_id == author_id).first()

    if book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete author because books are associated with this author."
        )

    author_query.delete(synchronize_session=False)
    db.commit()

    return {
        "message": "Author deleted successfully."
    }