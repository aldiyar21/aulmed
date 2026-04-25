from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class FacilitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.facilities"
    verbose_name = lang_text_lazy("Учреждения", "Ұйымдар")
