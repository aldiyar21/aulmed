from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = lang_text_lazy("Аудит", "Аудит")
