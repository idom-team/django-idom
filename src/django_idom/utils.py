import contextlib
import logging
import os
import re
from fnmatch import fnmatch
from importlib import import_module
from inspect import iscoroutinefunction
from typing import Callable, List, Set, Union

import idom
from django.http import HttpRequest
from django.template import engines
from django.urls import reverse
from django.utils.encoding import smart_str
from django.views import View
from idom import hooks, html, utils
from idom.types import ComponentType

from django_idom.config import IDOM_REGISTERED_COMPONENTS, IDOM_VIEW_COMPONENT_IFRAMES
from django_idom.types import ViewComponentIframe


COMPONENT_REGEX = re.compile(r"{% *component +((\"[^\"']*\")|('[^\"']*'))(.*?)%}")
_logger = logging.getLogger(__name__)


def view_to_component(
    view: Union[Callable, View],
    middleware: Union[List[Union[Callable, str]], None] = None,
    compatibility: bool = False,
    request: Union[HttpRequest, None] = None,
    *args,
    **kwargs,
) -> ComponentType:
    """Converts a Django view to an IDOM component.

    Args:
        middleware: The list of Django middleware to use when rendering the view.
            This can either be a list of middleware functions or string dotted paths.
        compatibility: If True, the component will be rendered in an iframe.
            This requires X_FRAME_OPTIONS = 'SAMEORIGIN' in settings.py.
        request: Request object to provide to the view.
        *args: The positional arguments to pass to the view.

    Keyword Args:
        **kwargs: The keyword arguments to pass to the view.
    """

    dotted_path = f"{view.__module__}.{view.__name__}".replace("<", "").replace(">", "")

    @idom.component
    def new_component():
        # Create a synthetic request object.
        request_obj = request
        if not request:
            request_obj = HttpRequest()
            request_obj.method = "GET"

        # Generate an iframe if compatibility mode is enabled.
        if compatibility:
            return html.iframe(
                {
                    "src": reverse("idom:view_to_component", args=[dotted_path]),
                    "loading": "lazy",
                }
            )

        # Hack for getting around some of Django's Async/Sync protections
        # Without this, we wouldn't be able to render async views within components
        async_view = False
        async_render, set_async_render = hooks.use_state(None)
        if async_render:
            return html._(
                utils.html_to_vdom(async_render.content.decode("utf-8").strip())
            )

        @hooks.use_effect(dependencies=[async_view])
        async def async_renderer():
            if async_view is True and not async_render:
                rendered_view = await _view_middleware(middleware, view)(
                    request_obj, *args, **kwargs
                )
                set_async_render(rendered_view)

        # Convert the view HTML to VDOM
        if isinstance(view, View):
            rendered_view = _view_middleware(middleware, view.as_view())(
                request_obj, *args, **kwargs
            )
            rendered_view.render()
        elif iscoroutinefunction(view):
            # Queue the view to be rendered within an UseEffect hook due to
            # async/sync limitations
            async_view = True
            return None
        else:
            rendered_view = _view_middleware(middleware, view)(
                request_obj, *args, **kwargs
            )

        return html._(utils.html_to_vdom(rendered_view.content.decode("utf-8").strip()))

    # Register an iframe if compatibility mode is enabled
    if compatibility:
        IDOM_VIEW_COMPONENT_IFRAMES[dotted_path] = ViewComponentIframe(
            middleware, view, new_component, args, kwargs
        )

    return new_component()


def _view_middleware(
    middleware: Union[List[Union[Callable, str]], None], view: Union[Callable, View]
) -> Callable:
    """Applies middleware to a view."""
    if not middleware:
        return view

    def _wrapper(*args, **kwargs):
        new_view = view
        for middleware_item in middleware:
            if isinstance(middleware_item, str):
                middleware_item = _import_dotted_path(middleware_item)
            new_view = middleware_item(new_view)(*args, **kwargs)
        return new_view

    return _wrapper


def _import_dotted_path(dotted_path: str) -> Callable:
    """Imports a dotted path and returns the callable."""
    module_name, component_name = dotted_path.rsplit(".", 1)

    try:
        module = import_module(module_name)
    except ImportError as error:
        raise RuntimeError(
            f"Failed to import {module_name!r} while loading {component_name!r}"
        ) from error

    try:
        return getattr(module, component_name)
    except AttributeError as error:
        raise RuntimeError(
            f"Module {module_name!r} has no component named {component_name!r}"
        ) from error


def _register_component(dotted_path: str) -> None:
    if dotted_path in IDOM_REGISTERED_COMPONENTS:
        return

    IDOM_REGISTERED_COMPONENTS[dotted_path] = _import_dotted_path(dotted_path)
    _logger.debug("IDOM has registered component %s", dotted_path)


class ComponentPreloader:
    def register_all(self):
        """Registers all IDOM components found within Django templates."""
        # Get all template folder paths
        paths = self._get_paths()
        # Get all HTML template files
        templates = self._get_templates(paths)
        # Get all components
        components = self._get_components(templates)
        # Register all components
        self._register_components(components)

    def _get_loaders(self):
        """Obtains currently configured template loaders."""
        template_source_loaders = []
        for e in engines.all():
            if hasattr(e, "engine"):
                template_source_loaders.extend(
                    e.engine.get_template_loaders(e.engine.loaders)
                )
        loaders = []
        for loader in template_source_loaders:
            if hasattr(loader, "loaders"):
                loaders.extend(loader.loaders)
            else:
                loaders.append(loader)
        return loaders

    def _get_paths(self) -> Set:
        """Obtains a set of all template directories."""
        paths = set()
        for loader in self._get_loaders():
            with contextlib.suppress(ImportError, AttributeError, TypeError):
                module = import_module(loader.__module__)
                get_template_sources = getattr(module, "get_template_sources", None)
                if get_template_sources is None:
                    get_template_sources = loader.get_template_sources
                paths.update(smart_str(origin) for origin in get_template_sources(""))
        return paths

    def _get_templates(self, paths: Set) -> Set:
        """Obtains a set of all HTML template paths."""
        extensions = [".html"]
        templates = set()
        for path in paths:
            for root, dirs, files in os.walk(path, followlinks=False):
                templates.update(
                    os.path.join(root, name)
                    for name in files
                    if not name.startswith(".")
                    and any(fnmatch(name, f"*{glob}") for glob in extensions)
                )

        return templates

    def _get_components(self, templates: Set) -> Set:
        """Obtains a set of all IDOM components by parsing HTML templates."""
        components = set()
        for template in templates:
            with contextlib.suppress(Exception):
                with open(template, "r", encoding="utf-8") as template_file:
                    match = COMPONENT_REGEX.findall(template_file.read())
                    if not match:
                        continue
                    components.update(
                        [group[0].replace('"', "").replace("'", "") for group in match]
                    )
        if not components:
            _logger.warning(
                "\033[93m"
                "IDOM did not find any components! "
                "You are either not using any IDOM components, "
                "using the template tag incorrectly, "
                "or your HTML templates are not registered with Django."
                "\033[0m"
            )
        return components

    def _register_components(self, components: Set) -> None:
        """Registers all IDOM components in an iterable."""
        for component in components:
            try:
                _logger.info("IDOM preloader has detected component %s", component)
                _register_component(component)
            except Exception:
                _logger.error(
                    "\033[91m"
                    "IDOM failed to register component '%s'! "
                    "This component path may not be valid, "
                    "or an exception may have occurred while importing."
                    "\033[0m",
                    component,
                )
