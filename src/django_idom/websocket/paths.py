from django.urls import path

from ..config import IDOM_WEBSOCKET_URL
from .consumer import IdomAsyncWebsocketConsumer


IDOM_WEBSOCKET_PATH = path(
    IDOM_WEBSOCKET_URL + "<view_id>/", IdomAsyncWebsocketConsumer.as_asgi()
)
"""A URL path for :class:`IdomAsyncWebsocketConsumer`.

Required in order for IDOM to know the websocket path.
"""
