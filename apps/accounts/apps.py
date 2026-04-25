from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = lang_text_lazy("Пользователи", "Пайдаланушылар")
