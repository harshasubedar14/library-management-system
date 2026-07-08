from sqlalchemy import TIMESTAMP, Column, Enum, Integer, String, func,Date,Text,CheckConstraint,ForeignKey,DateTime
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String(50),unique=True,nullable=False)
    email = Column(String(100),unique=True,nullable=False)
    password = Column(String(225),nullable=False)
    full_name = Column(String(100),nullable=False)
    role = Column(Enum('admin','user',name="user_role"),server_default='user')
    created_at = Column(TIMESTAMP(timezone=True),server_default=func.now())

    borrow_records = relationship("BorrowRecord", back_populates="user")
    reviews = relationship("Review", back_populates="user")

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    biography = Column(Text)
    nationality = Column(String(50))
    birth_date = Column(Date)

    books = relationship("Book", back_populates="author")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    books = relationship("Book", back_populates="category")

class Publisher(Base):
    __tablename__ = "publishers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    address = Column(String(255))
    contact_email = Column(String(100),unique=True,nullable=False)

    books = relationship("Book", back_populates="publisher")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    description = Column(Text)

    publication_year = Column(Integer)
    language = Column(String(30), server_default="English")

    total_copies = Column(Integer, nullable=False, server_default="1")
    available_copies = Column(Integer, nullable=False, server_default="1")
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    publisher_id = Column(Integer, ForeignKey("publishers.id"))

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "available_copies >= 0",
            name="check_available_copies_positive",
        ),
        CheckConstraint(
            "total_copies > 0",
            name="check_total_copies_positive",
        ),
        CheckConstraint(
            "available_copies <= total_copies",
            name="check_available_less_than_total",
        ),
    )
    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    borrow_records = relationship("BorrowRecord", back_populates="book")
    reviews = relationship("Review", back_populates="book")

class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    borrow_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)

    status = Column(
        Enum(
            "Borrowed",
            "Returned",
            "Overdue",
            name="borrow_status",
        ),
        nullable=False,
        server_default="Borrowed",
    )
    user = relationship("User", back_populates="borrow_records")
    book = relationship("Book", back_populates="borrow_records")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    rating = Column(Integer, nullable=False)
    review = Column(Text)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating",
        ),
    )
    user = relationship("User", back_populates="reviews")
    book = relationship("Book", back_populates="reviews")
    
