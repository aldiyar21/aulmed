from django.apps import AppConfig

from apps.core.i18n import lang_text_lazy


class ReferralsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.referrals"
    verbose_name = lang_text_lazy("Направления", "Жолдамалар")
