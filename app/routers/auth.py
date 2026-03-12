from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UpdateUserRequest
from app.services.auth import create_token, get_current_user, hash_password, verify_password

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


@router.get("/me")
def get_me(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": user.id,
            "username": user.username,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while loading profile") from exc


@router.put("/me")
def update_me(
    request: UpdateUserRequest,
    current_username: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.username == current_username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        has_username_change = request.username is not None and request.username.strip() != ""
        has_password_change = any(
            field is not None
            for field in (
                request.current_password,
                request.new_password,
                request.confirm_new_password,
            )
        )

        if not has_username_change and not has_password_change:
            raise HTTPException(status_code=422, detail="No profile updates provided")

        if has_username_change:
            new_username = request.username.strip()
            if new_username != user.username:
                existing = db.query(User).filter(User.username == new_username).first()
                if existing:
                    raise HTTPException(status_code=400, detail="Username already exists")
                user.username = new_username

        if has_password_change:
            if not request.current_password or not request.new_password or not request.confirm_new_password:
                raise HTTPException(
                    status_code=422,
                    detail="current_password, new_password and confirm_new_password are required",
                )

            if not verify_password(request.current_password, user.password):
                raise HTTPException(status_code=401, detail="Current password is incorrect")

            if request.new_password != request.confirm_new_password:
                raise HTTPException(status_code=422, detail="New passwords do not match")

            if request.current_password == request.new_password:
                raise HTTPException(
                    status_code=422,
                    detail="New password must be different from current password",
                )

            user.password = hash_password(request.new_password)

        db.commit()
        db.refresh(user)

        refreshed_token = create_token({"sub": user.username})
        return {
            "message": "Profile updated successfully",
            "id": user.id,
            "username": user.username,
            "access_token": refreshed_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating profile") from exc
