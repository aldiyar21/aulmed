from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class ReportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reports"
    verbose_name = lang_text_lazy("Отчеты", "Есептер")
