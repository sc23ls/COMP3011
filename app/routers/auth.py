from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth import create_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username cannot be empty")

    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        user = User(
            username=username,
            password=hash_password(request.password),
        )

        db.add(user)
        db.commit()
        return {"message": "User created successfully"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while registering user") from exc


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    username = request.username.strip()
    if not username:
        raise HTTPException(status_code=422, detail="Username cannot be empty")

    try:
        user = db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while fetching user") from exc

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token({"sub": user.username})
    return {
        "access_token": token,
        "token_type": "bearer",
    }
