from sqlalchemy.orm import Session
from app.models.user import User
from fastapi import HTTPException

class CreditService:
    @staticmethod
    def check_and_deduct(db: Session, user_id: str, amount: int = 1):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")
        if user.credits_remaining < amount:
            raise HTTPException(402, "No credits remaining")
        user.credits_remaining -= amount
        db.commit()
        return user.credits_remaining
