from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters.orm import mapper_registry
from domain.models import Product, User
from schemas.enums import Roles
from tests.integration.test_uow import insert_product, insert_user


def insert_tables_example(session):
    insert_product(session, Product("sku1", "name1", 1, "brand1", 1))
    insert_product(session, Product("sku2", "name2", 2, "brand2", 2))
    insert_user(
        session,
        User(
            email="super@test.com",
            username="super",
            password="password1",
            role=Roles.super_admin,
        ),
    )
    insert_user(
        session,
        User(
            email="admin@test.com",
            username="admin",
            password="password2",
            role=Roles.admin,
        ),
    )


def generate_sample_db(name):
    engine = create_engine(f"sqlite:///{name}.db")
    mapper_registry.metadata.drop_all(engine)
    mapper_registry.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    insert_tables_example(session)
    session.commit()


if __name__ == "__main__":
    generate_sample_db("product")
    print("Database generated!")
