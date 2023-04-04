import pytest
from fastapi import HTTPException

from domain import events
from domain.commands import user_commands, product_commands
from domain.models import Product, User, ProductSeen
from schemas.enums import Roles
from schemas.product import ProductSchema
from schemas.user import UserRegisterIn
from service_layer import messagebus
from tests.common import FakeUnitOfWork


class TestProductHandler:
    """Test ProductHandler"""

    @staticmethod
    def test_create_product():
        uow = FakeUnitOfWork()
        messagebus.handle(
            product_commands.CreateProduct(
                sku="test", name="test", price=10, brand="test", quantity=10
            ),
            uow,
        )

        assert uow.repository.get(Product, {"sku": "test"}) is not None
        assert uow.committed

    @staticmethod
    def test_create_product_already_exists():
        uow = FakeUnitOfWork()
        messagebus.handle(
            product_commands.CreateProduct(
                sku="test", name="test", price=10, brand="test", quantity=10
            ),
            uow,
        )
        with pytest.raises(HTTPException) as e:
            messagebus.handle(
                product_commands.CreateProduct(
                    sku="test", name="test", price=10, brand="test", quantity=10
                ),
                uow,
            )
        assert e.value.status_code == 400
        assert uow.committed

    @staticmethod
    def test_delete_product():
        uow = FakeUnitOfWork()
        messagebus.handle(
            product_commands.CreateProduct(
                sku="test", name="test", price=10, brand="test", quantity=10
            ),
            uow,
        )
        messagebus.handle(product_commands.DeleteProduct(sku="test"), uow)
        with pytest.raises(HTTPException) as e:
            uow.repository.get(Product, {"sku": "test"})
        assert uow.committed

    @staticmethod
    def test_update_product():
        uow = FakeUnitOfWork()
        messagebus.handle(
            product_commands.CreateProduct(
                sku="test", name="test", price=10, brand="test", quantity=10
            ),
            uow,
        )
        messagebus.handle(
            product_commands.UpdateProduct(
                sku="test",
                product=ProductSchema(
                    sku="test", name="test2", price=10, brand="test", quantity=10
                ),
            ),
            uow,
        )
        assert uow.repository.get(Product, {"sku": "test"}).name == "test2"
        assert uow.committed


class TestUserHandler:
    """Test UserHandler"""

    @staticmethod
    def test_register_user():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        assert uow.repository.get(User, {"email": "admin@test.com"}) is not None

    @staticmethod
    def test_register_user_already_exists():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        with pytest.raises(HTTPException) as e:
            messagebus.handle(
                user_commands.RegisterUser(
                    email="admin@test.com",
                    password="test",
                    username="admin",
                    role=Roles.admin,
                ),
                uow,
            )
        assert e.value.status_code == 400
        assert e.value.detail == "User already exists"

    @staticmethod
    def test_make_super_admin():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        messagebus.handle(user_commands.MakeUserSuperAdmin(email="admin@test.com"), uow)
        user = uow.repository.get(User, {"email": "admin@test.com"})
        assert user.role == Roles.super_admin

    @staticmethod
    def test_update_user():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        messagebus.handle(
            user_commands.UpdateUser(
                email="admin@test.com",
                new_user=UserRegisterIn(
                    email="admin@test.com",
                    password="test",
                    username="admin2",
                    role=Roles.admin,
                ),
            ),
            uow,
        )
        user = uow.repository.get(User, {"email": "admin@test.com"})
        assert user.username == "admin2"

    @staticmethod
    def test_delete_user():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        messagebus.handle(user_commands.DeleteUser(email="admin@test.com"), uow)
        with pytest.raises(HTTPException) as e:
            uow.repository.get(User, {"email": "admin@test.com"})
        assert e.value.status_code == 404
        assert e.value.detail == "The resource you are trying to access was not found"

    @staticmethod
    def test_register_viewed_product():
        uow = FakeUnitOfWork()
        messagebus.handle(
            user_commands.RegisterUser(
                email="admin@test.com",
                password="test",
                username="admin",
                role=Roles.admin,
            ),
            uow,
        )
        messagebus.handle(
            product_commands.CreateProduct(
                sku="test", name="test", price=10, brand="test", quantity=10
            ),
            uow,
        )
        messagebus.handle(
            events.ProductViewed(user_email="admin@test.com", sku="test"),
            uow,
        )
        product_seen = uow.repository.get(ProductSeen, {"product_sku": "test"})
        assert product_seen is not None
