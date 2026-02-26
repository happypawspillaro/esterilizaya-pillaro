from django.apps import AppConfig


class CampanaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "campana"

    def ready(self):
        import campana.signals  # noqa
