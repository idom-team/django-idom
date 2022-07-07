from django.urls import path

from . import views


app_name = "idom"

urlpatterns = [
    path(
        "web_module/<path:file>",
        views.web_modules_file,
        name="web_modules",
    ),
    path(
        "iframe/<str:view_path>",
        views.view_to_component_iframe,
        name="view_to_component",
    ),
]
