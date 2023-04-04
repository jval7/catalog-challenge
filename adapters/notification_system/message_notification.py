from abc import abstractmethod, ABC
from typing import Union

from domain import events


class AbstractMessageStrategy(ABC):
    @staticmethod
    @abstractmethod
    def create_message_and_subject(
        event: Union[
            events.ProductModified, events.ProductCreated, events.ProductDeleted
        ],
    ) -> (str, str):
        raise NotImplementedError


class ProductChangedStrategy(AbstractMessageStrategy):
    @staticmethod
    def create_message_and_subject(
        event: Union[
            events.ProductModified, events.ProductCreated, events.ProductDeleted
        ],
    ) -> (str, str):
        body = ProductChangedStrategy._create_body(event)
        subject = f"Product {event.sku} has been modified"
        return subject, body

    @staticmethod
    def _create_body(event):
        return (
            f"The product with sku: {event.sku} has been modified with the following "
            f"fields: {event.dict(exclude_none=True)}"
        )


class ProductCreatedStrategy(AbstractMessageStrategy):
    @staticmethod
    def create_message_and_subject(
        event: Union[
            events.ProductModified, events.ProductCreated, events.ProductDeleted
        ],
    ) -> (str, str):
        fields = event.dict()
        body = ProductCreatedStrategy._create_body(sku=event.sku, fields=fields)
        subject = f"Product {event.sku} has been created"
        return subject, body

    @staticmethod
    def _create_body(sku, fields: dict):
        return (
            f"The product with sku: {sku} has been created with the following "
            f"fields: {fields}"
        )


class ProductDeletedStrategy(AbstractMessageStrategy):
    @staticmethod
    def create_message_and_subject(
        event: Union[
            events.ProductModified, events.ProductCreated, events.ProductDeleted
        ],
    ) -> (str, str):
        body = f"The product with sku: {event.sku} has been deleted"
        subject = f"Product {event.sku} has been deleted"
        return subject, body


FACTORY_MESSAGE = {
    events.ProductCreated: ProductCreatedStrategy,
    events.ProductModified: ProductChangedStrategy,
    events.ProductDeleted: ProductDeletedStrategy,
}
