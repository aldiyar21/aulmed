from django.conf import settings
from django.db import models

from apps.core.i18n import lang_text_lazy


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audit_logs",
        verbose_name=lang_text_lazy("Пользователь", "Пайдаланушы"),
    )
    action = models.CharField(max_length=64, verbose_name=lang_text_lazy("Действие", "Әрекет"))
    entity_type = models.CharField(max_length=64, verbose_name=lang_text_lazy("Сущность", "Нысан"))
    entity_id = models.CharField(max_length=64, verbose_name=lang_text_lazy("ID сущности", "Нысан ID"))
    description = models.TextField(verbose_name=lang_text_lazy("Описание", "Сипаттама"))
    changes_json = models.JSONField(blank=True, null=True, verbose_name=lang_text_lazy("Изменения", "Өзгерістер"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=lang_text_lazy("Создано", "Құрылған"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = lang_text_lazy("Журнал аудита", "Аудит журналы")
        verbose_name_plural = lang_text_lazy("Журнал аудита", "Аудит журналы")
