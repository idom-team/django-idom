import os

from django.contrib.staticfiles.finders import find
from idom import component, html

from django_idom.config import IDOM_CACHE


@component
def django_css(static_path: str):
    """Fetches a CSS static file for use within IDOM. This allows for deferred CSS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would
        use on a `static` template tag.
    """
    return html.style(_cached_static_contents(static_path))


@component
def django_js(static_path: str):
    """Fetches a JS static file for use within IDOM. This allows for deferred JS loading.

    Args:
        static_path: The path to the static file. This path is identical to what you would
        use on a `static` template tag.
    """
    return html.script(_cached_static_contents(static_path))


def _cached_static_contents(static_path: str):
    # Try to find the file within Django's static files
    abs_path = find(static_path)
    if not abs_path:
        raise FileNotFoundError(
            f"Could not find static file {static_path} within Django's static files."
        )

    # Fetch the file from cache, if available
    # Cache is preferrable to `use_memo` due to multiprocessing capabilities
    last_modified_time = os.stat(abs_path).st_mtime
    cache_key = f"django_idom:static_contents:{static_path}"
    file_contents = IDOM_CACHE.get(cache_key, version=last_modified_time)
    if file_contents is None:
        with open(abs_path, encoding="utf-8") as static_file:
            file_contents = static_file.read()
        IDOM_CACHE.delete(cache_key)
        IDOM_CACHE.set(
            cache_key, file_contents, timeout=None, version=last_modified_time
        )

    return file_contents
