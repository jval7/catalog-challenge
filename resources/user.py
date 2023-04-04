from fastapi import APIRouter, Depends

from domain.commands import user_commands
from schemas.user import UserRegisterIn, UserLogin
from service_layer import messagebus
from service_layer.auth import oauth2_scheme, is_admin_or_super_admin, is_super_admin
from service_layer.unit_of_work import SqlalchemyUnitOfWork
from views import user_views

router = APIRouter(prefix="/user", tags=["users"])


@router.post(
    "/register",
    dependencies=[Depends(oauth2_scheme), Depends(is_super_admin)],
    status_code=201,
)
def register_user(user: UserRegisterIn):
    """
    Only super admin can register admin
    """
    cmd = user_commands.RegisterUser(**user.dict())
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "User registered successfully"}


@router.post("/login", status_code=200)
def login_user(user: UserLogin):
    """
    login user
    """
    token, role = user_views.login_user(user, SqlalchemyUnitOfWork())
    return {"token": token, "role": role}


@router.get(
    "/get_user/{email}",
    dependencies=[Depends(oauth2_scheme), Depends(is_admin_or_super_admin)],
    status_code=200,
)
def get_user(email: str):
    """
    get user by email
    """
    return user_views.get_user_by_email(email, SqlalchemyUnitOfWork())


@router.put(
    "/update_user/{email}",
    dependencies=[Depends(oauth2_scheme), Depends(is_super_admin)],
    status_code=200,
)
def update_user(email: str, user: UserRegisterIn):
    """
    update user
    """
    cmd = user_commands.UpdateUser(email, user)
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "User updated successfully"}


@router.delete(
    "/delete_user/{email}",
    dependencies=[Depends(oauth2_scheme), Depends(is_super_admin)],
    status_code=204,
)
def delete_user(email: str):
    """
    delete user
    """
    cmd = user_commands.DeleteUser(email)
    messagebus.handle(cmd, SqlalchemyUnitOfWork())


@router.put(
    "/change_role/{email}",
    dependencies=[Depends(oauth2_scheme), Depends(is_super_admin)],
    status_code=200,
)
def make_super_admin(email: str):
    """
    Make admin super admin
    """
    cmd = user_commands.MakeUserSuperAdmin(email)
    messagebus.handle(cmd, SqlalchemyUnitOfWork())
    return {"message": "User role changed successfully"}
