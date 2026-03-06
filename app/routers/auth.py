from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(request: RegisterRequest):

    db: Session = SessionLocal()

    existing = db.query(User).filter(User.username == request.username).first()

    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=request.username,
        password=hash_password(request.password)
    )

    db.add(user)
    db.commit()

    db.close()

    return {"message": "User created successfully"}


@router.post("/login")
def login(request: LoginRequest):

    db: Session = SessionLocal()

    user = db.query(User).filter(User.username == request.username).first()

    db.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token({"sub": user.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }