import pytest
from sqlalchemy.sql import text

from domain.models import Product, User
from schemas.enums import Roles
from service_layer.handler.user_handler import pwd_context
from service_layer.unit_of_work import SqlalchemyUnitOfWork


def insert_product(session, product: Product):
    session.execute(
        text(
            "INSERT INTO products (sku, name, price, brand, quantity)"
            " VALUES (:sku, :name, :price, :brand, :quantity)"
        ),
        dict(
            sku=product.sku,
            name=product.name,
            price=product.price,
            brand=product.brand,
            quantity=product.quantity,
        ),
    )


def insert_user(session, user: User):
    user.password = pwd_context.hash(user.password)
    session.execute(
        text(
            "INSERT INTO users (role, username, password, email)"
            " VALUES (:role, :username, :password, :email)"
        ),
        dict(
            role=user.role.name,
            username=user.username,
            password=user.password,
            email=user.email,
        ),
    )


def test_uow_can_retrieve_products_and_users(session_factory):
    # Arrange
    session = session_factory()
    uow = SqlalchemyUnitOfWork(session_factory)
    insert_product(
        session,
        Product(
            sku="123", name="Harry Potter", price=10, brand="J.K. Rowling", quantity=10
        ),
    )
    insert_user(
        session,
        User(
            role=Roles.admin,
            username="admin",
            password="admin",
            email="admin1@test.com",
        ),
    )
    session.commit()

    # Act
    with uow:
        product = uow.repository.get(Product, {"sku": "123"})
        user = uow.repository.get(User, {"email": "admin1@test.com"})
        assert product.sku == "123"
        assert user.username == "admin"


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = SqlalchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_product(
                uow.session,
                Product(
                    sku="123",
                    name="Harry Potter",
                    price=10,
                    brand="J.K. Rowling",
                    quantity=10,
                ),
            )
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "products"')))
    assert rows == []
