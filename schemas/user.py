from pydantic import BaseModel

from schemas.enums import Roles


class UserBase(BaseModel):
    email: str


class UserLogin(UserBase):
    password: str


class UserRegisterIn(UserLogin):
    role: Roles
    username: str

    class Config:
        orm_mode = True


class UserOut(UserBase):
    username: str
    role: Roles

    class Config:
        orm_mode = True
