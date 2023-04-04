import abc
from typing import Union, Set

from fastapi import HTTPException
from sqlalchemy import delete, select
from starlette import status

from domain.models import Product, User, ProductSeen
from logger import logger


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Union[Set[Product], Set[User]]

    def add(self, row: Union[Product, User, ProductSeen]):
        self._add(row)
        self.seen.add(row)

    def get(
        self,
        table: Union[type[Product], type[User], type[ProductSeen]],
        dict_to_filter: dict,
    ) -> Union[Product, User, ProductSeen]:
        row = self._get(table, dict_to_filter)
        if row:
            self.seen.add(row)
        return row

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, row: Union[Product, User, ProductSeen]):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(
        self,
        table: Union[type[Product], type[User], type[ProductSeen]],
        dict_to_filter: dict,
    ) -> Union[Product, User, ProductSeen]:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    def _add(self, row):
        """
        this function saves a row in a table
        Args:
            row: table name
        Returns:

        """
        self.session.add(row)
        self.session.flush([row])
        # session.refresh(self)

    def delete(self, table, column_name: str, column_value: str):
        """
        this function deletes a row in a table filtering by column_name and column_value
        Args:
            table: table name
            column_name: the name of the column to be compared
            column_value: the value of the column to be compared
        Returns: the number of rows deleted

        """
        statement = delete(table).where(table.__dict__[column_name] == column_value)
        response = self.session.execute(statement)
        return response.rowcount

    def _get(self, table, dict_to_filter: dict):
        """
        this function filters a table by dict_to_filter and returns the first row
        Args:
            table: table name
            dict_to_filter: a dict to filter, we can use multiple variables to filter {var1:val1,var2:val2}

        Returns: row

        """
        statement = select(table).filter_by(**dict_to_filter)
        response = self.session.execute(statement).scalar()
        if not response:
            logger.error(f"Error trying to get {table} with {dict_to_filter}")
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "The resource you are trying to access was not found",
            )
        return response
