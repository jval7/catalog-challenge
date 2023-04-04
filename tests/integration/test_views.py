from domain.commands import user_commands, product_commands
from schemas.enums import Roles
from schemas.user import UserLogin
from service_layer import messagebus
from service_layer.unit_of_work import SqlalchemyUnitOfWork
from views import user_views, product_views


def test_login_view(session_factory):
    uow = SqlalchemyUnitOfWork(session_factory)
    messagebus.handle(
        user_commands.RegisterUser(
            username="admin",
            password="admin",
            email="admin@test.com",
            role=Roles.super_admin,
        ),
        uow,
    )

    _, role = user_views.login_user(
        UserLogin(email="admin@test.com", password="admin"), uow
    )
    assert role == Roles.super_admin


def test_get_user_by_email_view(session_factory):
    uow = SqlalchemyUnitOfWork(session_factory)
    messagebus.handle(
        user_commands.RegisterUser(
            username="admin",
            password="admin",
            email="admin@test.com",
            role=Roles.super_admin,
        ),
        uow,
    )

    user = user_views.get_user_by_email("admin@test.com", uow)
    assert user.email == "admin@test.com"


def test_get_product(session_factory):
    uow = SqlalchemyUnitOfWork(session_factory)
    messagebus.handle(
        product_commands.CreateProduct(
            sku="test", name="test", price=10, brand="test", quantity=10
        ),
        uow,
    )

    product = product_views.get_product(sku="test", uow=uow)

    assert product.sku == "test"
