from pydantic import BaseModel,EmailStr, Field
from typing import  Literal
from datetime import date,timedelta
from typing import Optional

class CreateUser(BaseModel):
    username : str
    email : EmailStr
    password : str
    full_name : str
    role: Literal['user', 'admin'] = Field(default='user')

class PasswordUpdate(BaseModel):
    username : str
    old_password : str
    new_password : str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    user_id : int

class AuthorCreate(BaseModel):
    name : str
    biography : str
    nationality : str
    birth_date : date

class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str
    description: str | None = None

class Publisher(BaseModel):
    name : str
    address : str
    contact_email : EmailStr

class PublisherCreate(BaseModel):
    name: str
    address: str | None = None
    contact_email: str | None = None


class PublisherUpdate(BaseModel):
    name: str
    address: str | None = None
    contact_email: str | None = None

class BookCreate(BaseModel):
    title: str
    isbn: str
    description: str | None = None
    publication_year: int | None = None
    language: str = "English"
    total_copies: int
    available_copies: int
    author_id: int
    category_id: int
    publisher_id: int

class BookUpdate(BaseModel):
    title: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None
    language: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    publisher_id: Optional[int] = None

class BorrowBook(BaseModel):
    book_id: int
    due_date: date = Field(
        default_factory=lambda: date.today() + timedelta(days=7)
    )

class ReviewCreate(BaseModel):
    book_id: int
    rating: int = Field(..., ge=1, le=5)
    review: str

