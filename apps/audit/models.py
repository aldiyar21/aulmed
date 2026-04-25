from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audit_logs",
        verbose_name="Пользователь",
    )
    action = models.CharField(max_length=64, verbose_name="Действие")
    entity_type = models.CharField(max_length=64, verbose_name="Сущность")
    entity_id = models.CharField(max_length=64, verbose_name="ID сущности")
    description = models.TextField(verbose_name="Описание")
    changes_json = models.JSONField(blank=True, null=True, verbose_name="Изменения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Журнал аудита"
        verbose_name_plural = "Журнал аудита"
