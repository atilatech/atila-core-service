from django.apps import AppConfig


class AtlasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'atlas'

    def ready(self):
        # Makes sure all signal handlers are connected
        from atlas import handlers  # noqa