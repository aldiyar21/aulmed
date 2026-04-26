from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Ядро"

    def ready(self) -> None:
        from apps.core.runtime_translations import install_runtime_translations

        install_runtime_translations()
