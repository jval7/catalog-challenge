from dataclasses import dataclass

from domain.commands.product_commands import Command
from schemas.enums import Roles
from schemas.user import UserRegisterIn


@dataclass
class RegisterUser(Command):
    email: str
    password: str
    username: str
    role: Roles


@dataclass
class MakeUserSuperAdmin(Command):
    email: str


@dataclass
class UpdateUser(Command):
    email: str
    new_user: UserRegisterIn


@dataclass
class DeleteUser(Command):
    email: str
