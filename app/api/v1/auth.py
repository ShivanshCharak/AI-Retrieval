from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from app.db.models import User
from sqlalchemy.orm import Session
from sqlalchemy import select
import jwt
from fastapi import Response
from datetime import datetime, timedelta, timezone

from app.db.database import get_db
from pwdlib import PasswordHash

router = APIRouter()

password_hash = PasswordHash.recommended()
SECRET_KEY = "4WfP4JbL6lLQ5zQZ_8K4YxW5RkM8bM7T9dN2L8xR1cA"


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class SigninRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
async def signup(
    data: SignupRequest, response: Response, db: Session = Depends(get_db)
):
    if not data.email or not data.name or not data.password:
        raise HTTPException(status_code=400, detail="Fields are missing")
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(status_code=409, detail="Emails already exist")
    try:
        user = User(
            name=data.name,
            email=data.email,
            password_hash=password_hash.hash(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"status_code": 200, "id": user.id, "message": "user_created"}
    except:
        db.rollback()
        raise HTTPException(status_code=500, details="Something went wrong")


@router.post("/signin")
async def signin(
    data: SigninRequest, response: Response, db: Session = Depends(get_db)
):
    print(data)
    if not data.email or not data.password:
        raise HTTPException(status_code=500, detail="fields are missing")
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None:
        raise HTTPException(status_code=401, detail="invalid email or password")
    print(user)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    if not password_hash.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3000,
    )
    return {"status": 200, "detail": "login sucesffull"}


@router.get("/me")
async def me(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.scalar(select(User).where(User.email == payload["email"]))
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": user.name, "email": user.email, "id": user.id}
