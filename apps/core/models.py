from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActiveQuerySet(models.QuerySet):
    def active(self) -> "ActiveQuerySet":
        return self.filter(is_active=True)


class SoftDeleteModel(TimeStampedModel):
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    objects = ActiveQuerySet.as_manager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    notification_type = models.CharField(max_length=64, verbose_name="Тип")
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Текст")
    due_date = models.DateField(blank=True, null=True, verbose_name="Срок")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата прочтения")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def mark_as_read(self) -> None:
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])
