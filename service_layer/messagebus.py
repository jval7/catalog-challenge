from __future__ import annotations

import logging
from typing import List, Dict, Callable, Type, Union

from domain import commands
from domain import events
from domain.commands import product_commands, user_commands
from service_layer.handler.product_handler import ProductHandler
from service_layer.handler.user_handler import UserHandler
from service_layer.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle(
    message: Message,
    uow: AbstractUnitOfWork,
):
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            handle_command(message, queue, uow)
        else:
            raise Exception(f"{message} was not an Event or Command")


def handle_event(
    event: events.Event,
    queue: List[Message],
    uow: AbstractUnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("handling event %s with handler %s", event, handler)
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue


def handle_command(
    command: commands.Command,
    queue: List[Message],
    uow: AbstractUnitOfWork,
):
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


EVENT_HANDLERS = {
    events.ProductViewed: [UserHandler.register_view],
    events.ProductModified: [UserHandler.notify_product_change_to_all_users],
    events.ProductDeleted: [UserHandler.notify_product_change_to_all_users],
    events.ProductCreated: [UserHandler.notify_product_change_to_all_users],
}  # type: Dict[Type[events.Event], List[Callable]]

COMMAND_HANDLERS = {
    product_commands.CreateProduct: ProductHandler.create_product,
    product_commands.UpdateProduct: ProductHandler.update_product,
    product_commands.DeleteProduct: ProductHandler.delete_product,
    # user commands
    user_commands.RegisterUser: UserHandler.register_user,
    user_commands.MakeUserSuperAdmin: UserHandler.make_super_admin,
    user_commands.DeleteUser: UserHandler.delete_user,
    user_commands.UpdateUser: UserHandler.update_user,
}  # type: Dict[Type[commands.Command], Callable]
