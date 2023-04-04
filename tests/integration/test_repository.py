from adapters.repositories.repository import SQLAlchemyRepository
from domain.models import Product, User
from schemas.enums import Roles


def test_get_by_sku(sqlite_session):
    repo = SQLAlchemyRepository(sqlite_session)
    product = Product(
        sku="123", name="Harry Potter", price=10, brand="J.K. Rowling", quantity=10
    )
    user = User(
        role=Roles.admin, username="admin", password="admin", email="admin@test.com"
    )

    repo.add(product)
    repo.add(user)
    assert repo.get(Product, {"sku": "123"}) == product
    assert repo.get(User, {"email": "admin@test.com"}) == user
