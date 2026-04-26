from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class PreventionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prevention"
    verbose_name = lang_text_lazy("Профилактика", "Профилактика")
