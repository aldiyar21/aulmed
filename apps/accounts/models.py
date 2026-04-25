from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class EmployeeProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ("admin", "Администратор"),
        ("registrar", "Регистратор"),
        ("clinician", "Медработник"),
        ("manager", "Руководитель"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="Пользователь",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
        verbose_name="Учреждение",
    )
    position = models.CharField(max_length=255, verbose_name="Должность")
    role_code = models.CharField(max_length=32, choices=ROLE_CHOICES, verbose_name="Роль")
    phone = models.CharField(max_length=32, blank=True, verbose_name="Телефон")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username
