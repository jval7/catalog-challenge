from typing import Union

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from adapters.notification_system.message_notification import (
    AbstractMessageStrategy,
    FACTORY_MESSAGE,
)
from adapters.notification_system.notification_strategies import (
    EmailNotification,
    AbstractNotification,
)
from domain import events
from domain.commands import user_commands
from domain.models import User, ProductSeen
from logger import logger
from schemas.enums import Roles
from schemas.user import UserRegisterIn
from service_layer.unit_of_work import AbstractUnitOfWork

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserHandler:
    """This class is responsible for all admin related operations"""

    @staticmethod
    def register_user(cmd: user_commands.RegisterUser, uow: AbstractUnitOfWork):
        """Create a new user"""
        with uow:
            logger.info("Creating user")
            user = User(
                email=cmd.email,
                username=cmd.username,
                password=pwd_context.hash(cmd.password),
                role=cmd.role,
            )
            try:
                uow.repository.add(user)
            except IntegrityError:
                logger.error("User already exists")
                raise HTTPException(status_code=400, detail="User already exists")

    @staticmethod
    def make_super_admin(
        cmd: user_commands.MakeUserSuperAdmin, uow: AbstractUnitOfWork
    ):
        """Change user role to super admin"""
        with uow:
            logger.info("Changing user role")
            user = uow.repository.get(User, dict_to_filter={"email": cmd.email})
            user.role = Roles.super_admin

    @staticmethod
    def update_user(cmd: user_commands.UpdateUser, uow: AbstractUnitOfWork):
        """Update user"""
        with uow:
            logger.info("Updating user")
            try:
                user = uow.repository.get(User, dict_to_filter={"email": cmd.email})
                UserHandler._update_user_inplace(user, cmd.new_user)
                uow.commit()
            except IntegrityError:
                logger.error(
                    "Bad request, check the parameters, remember that email must be unique"
                )
                raise HTTPException(
                    status_code=400,
                    detail="Bad request, check the parameters, remember that email "
                    "must be unique",
                )

    @staticmethod
    def _update_user_inplace(user: User, updated_user: UserRegisterIn):
        user.username = updated_user.username
        user.role = updated_user.role
        user.email = updated_user.email
        user.password = pwd_context.hash(updated_user.password)

    @staticmethod
    def delete_user(cmd: user_commands.DeleteUser, uow: AbstractUnitOfWork):
        """Delete user"""
        with uow:
            logger.info("Deleting user")
            deleted_users_number = uow.repository.delete(User, "email", cmd.email)
            if deleted_users_number == 0:
                logger.error("User not found")
                raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def register_view(event: events.ProductViewed, uow: AbstractUnitOfWork):
        """Create view"""
        with uow:
            if not event.user_email:
                user = User(email="anonymous", role=Roles.anonymous)
            else:
                user = uow.repository.get(
                    User, dict_to_filter={"email": event.user_email}
                )
            logger.info("Creating view")
            product_seen = ProductSeen(
                product_sku=event.sku, user_email=user.email, role=user.role
            )
            uow.repository.add(product_seen)

    @staticmethod
    def notify_product_change_to_all_users(
        event: Union[
            events.ProductModified, events.ProductCreated, events.ProductDeleted
        ],
        uow: AbstractUnitOfWork,
        message_strategy: AbstractMessageStrategy = None,
        sender_strategy: AbstractNotification = None,
    ):
        """Notify users about product change"""
        message_strategy = message_strategy or FACTORY_MESSAGE[type(event)]
        sender_strategy = sender_strategy or EmailNotification
        with uow:
            addressees = list(uow.session.execute(text("SELECT email FROM users")))
            addressees = [row[0] for row in addressees]
            subject, body = message_strategy.create_message_and_subject(event)
            sender_strategy.send(addressees, subject, body)
