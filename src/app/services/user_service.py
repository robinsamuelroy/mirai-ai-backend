# src/app/services/user_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.utils.hashing import verify_password
from app.utils.jwt import create_access_token


class UserService:

    def register(self, db: Session, data: UserCreate) -> User:
        """
        Registration logic:
        1. Check if email already exists
        2. If yes → raise error
        3. If no → create user
        """
        existing = user_repository.get_by_email(db, data.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
                # Django comparison: similar to ValidationError in serializers
            )

        return user_repository.create(db, data)

    def get_user(self, db: Session, user_id: int) -> User:
        """Fetch a user or raise 404 if not found"""
        user = user_repository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user



    def login(self, db: Session, data: UserLogin) -> dict:
        user = user_repository.get_by_email(db, data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

# single shared instance
user_service = UserService()