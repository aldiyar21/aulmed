from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class EncountersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.encounters"
    verbose_name = lang_text_lazy("Обращения", "Қабылдаулар")
