from functools import wraps
from typing import Callable, Union

from idom.core.types import ComponentType, VdomDict

from django_idom.hooks import use_websocket


def auth_required(
    component: Union[Callable, None] = None,
    auth_attribute: str = "is_active",
    fallback: Union[ComponentType, VdomDict, None] = None,
) -> Callable:
    """If the user passes authentication criteria, the decorated component will be rendered.
    Otherwise, the fallback component will be rendered.

    This decorator can be used with or without parentheses.

    Args:
        auth_attribute: The value to check within the user object.
            This is checked in the form of `UserModel.<auth_attribute>`.
        fallback: The component or VDOM (`idom.html` snippet) to render if the user is not authenticated.
    """

    def decorator(component):
        @wraps(component)
        def _wrapped_func(*args, **kwargs):
            websocket = use_websocket()

            if getattr(websocket.scope["user"], auth_attribute):
                return component(*args, **kwargs)

            if callable(fallback):
                return fallback(*args, **kwargs)
            return fallback

        return _wrapped_func

    # Return for @authenticated(...)
    if component is None:
        return decorator

    # Return for @authenticated
    return decorator(component)
