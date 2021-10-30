from django.apps import AppConfig

from .utils import ComponentPreloader


class HomeConfig(AppConfig):
    name = "django_idom"

    def ready(self):
        # Populate the IDOM component registry when Django is ready
        ComponentPreloader().register_all()
