from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.hashing import hash_password

class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()
    
    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()
    
    def create(self, db: Session, data: UserCreate) -> User:
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password))
        db.add(user)       # stage the insert
        db.commit()        # write to database
        db.refresh(user)   # reload from DB so id and created_at are populated
        return user

user_repository = UserRepository()