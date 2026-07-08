from fastapi import FastAPI

from app.routes import category
from .routes import authors, user,auth

app = FastAPI()

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(category.router)