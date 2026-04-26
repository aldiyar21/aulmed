from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class VisitsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.visits"
    verbose_name = lang_text_lazy("Выезды на дом", "Үйге барулар")
