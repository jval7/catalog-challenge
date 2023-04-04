from datetime import datetime, timedelta

import jwt
from decouple import config
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request

from domain.models import User
from logger import logger
from schemas.enums import Roles
from schemas.user import UserRegisterIn
from service_layer.unit_of_work import SqlalchemyUnitOfWork


class AuthManager:
    @staticmethod
    def encode_token(user: User):
        try:
            payload = {
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(minutes=120),
            }
            return jwt.encode(payload, config("SECRET_KEY"), algorithm="HS256")
        except Exception as ex:
            logger.error(f"Error while encoding token: {ex}")
            raise ex

    @staticmethod
    def get_user_from_token(credentials, request, uow):
        """
        Get user from token
        Args:
            credentials:
            request:
            uow:

        Returns:

        """
        try:
            payload = jwt.decode(
                credentials, config("SECRET_KEY"), algorithms=["HS256"]
            )
            user_data = uow.repository.get(
                User, dict_to_filter={"email": payload["email"]}
            )
            request.state.user = user_data
            return user_data
        except jwt.ExpiredSignatureError:
            raise HTTPException(401, "Token is expired")
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")


class CustomHHTPBearer(HTTPBearer):
    """
    Custom HTTP Bearer class to handle user authentication
    """

    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        _, credentials = get_authorization_scheme_param(authorization)
        uow = SqlalchemyUnitOfWork()
        if credentials:
            with uow:
                user_data = AuthManager.get_user_from_token(credentials, request, uow)

                request.state.user = UserRegisterIn.from_orm(user_data)
        else:
            request.state.user = User(role=Roles.anonymous, email="")


oauth2_scheme = CustomHHTPBearer()


def is_admin(request: Request):
    if not request.state.user.role == Roles.admin:
        raise HTTPException(403, "Forbidden")


def is_super_admin(request: Request):
    if not request.state.user.role == Roles.super_admin:
        raise HTTPException(403, "Forbidden")


def is_admin_or_super_admin(request: Request):
    if not request.state.user.role in [Roles.admin, Roles.super_admin]:
        raise HTTPException(403, "Forbidden")
