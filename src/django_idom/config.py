from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from idom.core.types import ComponentConstructor

from django_idom.types import ViewComponentIframe


IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}
IDOM_VIEW_COMPONENT_IFRAMES: Dict[str, ViewComponentIframe] = {}

IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "idom/")
IDOM_WS_MAX_RECONNECT_TIMEOUT = getattr(
    settings, "IDOM_WS_MAX_RECONNECT_TIMEOUT", 604800
)

# Determine if using Django caching or LRU cache
if "idom" in getattr(settings, "CACHES", {}):
    IDOM_CACHE = caches["idom"]
else:
    IDOM_CACHE = caches[DEFAULT_CACHE_ALIAS]
