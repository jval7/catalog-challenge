from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import text

from logger import logger
from schemas.user import UserLogin, UserOut
from service_layer.auth import AuthManager
from service_layer.unit_of_work import AbstractUnitOfWork

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login_user(user: UserLogin, uow: AbstractUnitOfWork):
    """Login user"""
    with uow:
        logger.info("Logging in user")
        try:
            user_database = next(
                uow.session.execute(
                    text("SELECT * FROM users WHERE email = :email"),
                    {"email": user.email},
                )
            )
        except StopIteration:
            logger.error("User not found")
            raise HTTPException(status_code=400, detail="Wrong email or password")
        if not pwd_context.verify(user.password, user_database.password):
            logger.error("Wrong password")
            raise HTTPException(status_code=400, detail="Wrong email or password")
        return AuthManager.encode_token(user_database), user_database.role


def get_user_by_email(email: str, uow: AbstractUnitOfWork) -> UserOut:
    """Get user by email"""
    with uow:
        logger.info("Getting user by email")
        try:
            user = next(
                uow.session.execute(
                    text("SELECT * FROM users WHERE email = :email"), {"email": email}
                )
            )
        except StopIteration:
            logger.error("User not found")
            raise HTTPException(status_code=404, detail="User not found")
        return UserOut.from_orm(user)
