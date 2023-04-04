from fastapi import HTTPException
from starlette import status

from adapters.repositories.repository import AbstractRepository
from service_layer.unit_of_work import AbstractUnitOfWork


class FakeRepository(AbstractRepository):
    def __init__(self):
        super().__init__()
        self._fake_db_dict = {
            "products": set(),
            "users": set(),
            "product_seen": set(),
        }

    def _add(self, table):
        table_name = table.__tablename__
        evaluation = "email" if table_name == "users" else "sku"
        for row in self._fake_db_dict[table_name]:
            if getattr(row, evaluation) == getattr(table, evaluation):
                raise HTTPException(status_code=400, detail="User already exists")
        self._fake_db_dict[table_name].add(table)

    def _get(self, table, dict_to_filter):
        table_name = table.__tablename__
        for row in self._fake_db_dict[table_name]:
            for key, value in dict_to_filter.items():
                if getattr(row, key) == value:
                    return row
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "The resource you are trying to access was not found",
        )

    def delete(self, table, column_name, column_value):
        table_name = table.__tablename__
        rowcount = 0
        to_remove = []
        for row in self._fake_db_dict[table_name]:
            if getattr(row, column_name) == column_value:
                to_remove.append(row)
                rowcount += 1
        for row in to_remove:
            self._fake_db_dict[table_name].remove(row)
        return rowcount


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        super().__init__()
        self.roll_backed = None
        self.repository = FakeRepository()
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        self.roll_backed = True
