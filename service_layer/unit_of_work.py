from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from adapters.repositories import repository
from adapters.repositories.repository import SQLAlchemyRepository
from logger import logger


class AbstractUnitOfWork(ABC):
    repository: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, exn_type, exn_value, traceback):
        if exn_type:
            self.rollback()
        else:
            self.commit()

    def collect_new_events(self):
        for object_seen in self.repository.seen:
            while object_seen.events:
                yield object_seen.events.pop(0)

    def commit(self):
        self._commit()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


SESSION_FACTORY = sessionmaker(bind=create_engine(config.get_db_connection_string()))


class SqlalchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=SESSION_FACTORY):
        super().__init__()
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        logger.info("Database Session was created")
        self.repository = SQLAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        logger.info("Database Session closed")
        self.session.close()

    def _commit(self):
        logger.info("Committing changes to database")
        self.session.commit()

    def rollback(self):
        logger.info("Rolling back changes to database")
        self.session.rollback()
