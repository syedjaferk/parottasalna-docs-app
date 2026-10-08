from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr


@app.post("/users", response_model=UserOut)
def create_user(user: UserCreate):
    # FastAPI has already validated `user` against UserCreate before this line runs
    new_user = {"id": 1, "username": user.username, "email": user.email}
    return new_user  # FastAPI validates/filters this against UserOut before sending it
