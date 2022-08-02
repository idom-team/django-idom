from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    DefaultDict,
    Generic,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
)

from channels.db import database_sync_to_async as _database_sync_to_async
from django.db.models.base import Model
from django.db.models.query import QuerySet
from idom import use_callback, use_ref
from idom.backend.types import Location
from idom.core.hooks import Context, create_context, use_context, use_effect, use_state
from typing_extensions import ParamSpec

from django_idom.types import IdomWebsocket


database_sync_to_async = cast(
    Callable[..., Callable[..., Awaitable[Any]]],
    _database_sync_to_async,
)

_REFETCH_CALLBACKS: DefaultDict[
    Callable[..., Any], set[Callable[[], None]]
] = DefaultDict(set)
WebsocketContext: Type[Context[Union[IdomWebsocket, None]]] = create_context(
    None, "WebSocketContext"
)
_Result = TypeVar("_Result", bound=Union[Model, QuerySet[Any]])
_Params = ParamSpec("_Params")
_Data = TypeVar("_Data")


def use_location() -> Location:
    """Get the current route as a string"""
    # TODO: Use the browser's current page, rather than the WS route
    scope = use_scope()
    search = scope["query_string"].decode()
    return Location(scope["path"], f"?{search}" if search else "")


def use_scope() -> dict[str, Any]:
    """Get the current ASGI scope dictionary"""
    return use_websocket().scope


def use_websocket() -> IdomWebsocket:
    """Get the current IdomWebsocket object"""
    websocket = use_context(WebsocketContext)
    if websocket is None:
        raise RuntimeError("No websocket. Are you running with a Django server?")
    return websocket


def use_query(
    query: Callable[_Params, _Result | None],
    *args: _Params.args,
    **kwargs: _Params.kwargs,
) -> Query[_Result | None]:
    query_ref = use_ref(query)
    if query_ref.current is not query:
        raise ValueError(f"Query function changed from {query_ref.current} to {query}.")

    should_execute, set_should_execute = use_state(True)
    data, set_data = use_state(cast(Union[_Result, None], None))
    loading, set_loading = use_state(True)
    error, set_error = use_state(cast(Union[Exception, None], None))

    @use_callback
    def refetch() -> None:
        set_should_execute(True)
        set_loading(True)
        set_error(None)

    @use_effect(dependencies=[])
    def add_refetch_callback() -> Callable[[], None]:
        # By tracking callbacks globally, any usage of the query function will be re-run
        # if the user has told a mutation to refetch it.
        _REFETCH_CALLBACKS[query].add(refetch)
        return lambda: _REFETCH_CALLBACKS[query].remove(refetch)

    @use_effect(dependencies=None)
    @database_sync_to_async
    def execute_query() -> None:
        if not should_execute:
            return

        try:
            new_data = query(*args, **kwargs)
            _fetch_deferred(new_data)
        except Exception as e:
            set_data(None)
            set_loading(False)
            set_error(e)
            return
        finally:
            set_should_execute(False)

        set_data(new_data)
        set_loading(False)
        set_error(None)

    return Query(data, loading, error, refetch)


def use_mutation(
    mutate: Callable[_Params, bool | None],
    refetch: Callable[..., Any] | Sequence[Callable[..., Any]],
) -> Mutation[_Params]:
    loading, set_loading = use_state(False)
    error, set_error = use_state(cast(Union[Exception, None], None))

    @use_callback
    def call(*args: _Params.args, **kwargs: _Params.kwargs) -> None:
        set_loading(True)

        @database_sync_to_async
        def execute_mutation() -> None:
            try:
                should_refetch = mutate(*args, **kwargs)
            except Exception as e:
                set_loading(False)
                set_error(e)
            else:
                set_loading(False)
                set_error(None)
                if should_refetch is not False:
                    for query in (refetch,) if callable(refetch) else refetch:
                        for callback in _REFETCH_CALLBACKS.get(query) or ():
                            callback()

        asyncio.ensure_future(execute_mutation())

    @use_callback
    def reset() -> None:
        set_loading(False)
        set_error(None)

    return Mutation(call, loading, error, reset)


@dataclass
class Query(Generic[_Data]):
    data: _Data
    loading: bool
    error: Exception | None
    refetch: Callable[[], None]


@dataclass
class Mutation(Generic[_Params]):
    execute: Callable[_Params, None]
    loading: bool
    error: Exception | None
    reset: Callable[[], None]


def _fetch_deferred(data: Any) -> None:
    # https://github.com/typeddjango/django-stubs/issues/704
    if isinstance(data, QuerySet):  # type: ignore[misc]
        for model in data:
            _fetch_deferred_model_fields(model)
    elif isinstance(data, Model):
        _fetch_deferred_model_fields(data)
    else:
        raise ValueError(f"Expected a Model or QuerySet, got {data!r}")


def _fetch_deferred_model_fields(model: Any) -> None:
    for field in model.get_deferred_fields():
        value = getattr(model, field)
        if isinstance(value, Model):
            _fetch_deferred_model_fields(value)
