import os
from typing import Dict

from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from idom.core.types import ComponentConstructor


os.environ["IDOM_DEBUG_MODE"] = str(int(settings.DEBUG))

IDOM_REGISTERED_COMPONENTS: Dict[str, ComponentConstructor] = {}

IDOM_WEBSOCKET_URL = getattr(settings, "IDOM_WEBSOCKET_URL", "idom/")
IDOM_WS_MAX_RECONNECT_TIMEOUT = getattr(
    settings, "IDOM_WS_MAX_RECONNECT_TIMEOUT", 604800
)

# Determine if using Django caching or LRU cache
if "idom" in getattr(settings, "CACHES", {}):
    IDOM_CACHE = caches["idom"]
else:
    IDOM_CACHE = caches[DEFAULT_CACHE_ALIAS]
