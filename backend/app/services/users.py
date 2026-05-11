from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db import models, schemas # Assuming you have Pydantic schemas

# Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate):
        """
        Creates a new user and hashes their password.
        """
        hashed_pw = UserService.get_password_hash(user.password)
        
        db_user = models.User(
            email=user.email,
            hashed_password=hashed_pw,
            full_name=user.full_name,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

# Usage: UserService.create_user(db, user_data)