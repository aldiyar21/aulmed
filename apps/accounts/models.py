from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class EmployeeProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ("admin", lang_text_lazy("Администратор", "Әкімші")),
        ("registrar", lang_text_lazy("Регистратор", "Тіркеуші")),
        ("clinician", lang_text_lazy("Медработник", "Медицина қызметкері")),
        ("manager", lang_text_lazy("Руководитель", "Басшы")),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name=lang_text_lazy("Пользователь", "Пайдаланушы"),
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
        verbose_name=lang_text_lazy("Учреждение", "Ұйым"),
    )
    position = models.CharField(max_length=255, verbose_name=lang_text_lazy("Должность", "Лауазымы"))
    role_code = models.CharField(max_length=32, choices=ROLE_CHOICES, verbose_name=lang_text_lazy("Роль", "Рөлі"))
    phone = models.CharField(max_length=32, blank=True, verbose_name=lang_text_lazy("Телефон", "Телефон"))
    is_active = models.BooleanField(default=True, verbose_name=lang_text_lazy("Активен", "Белсенді"))

    class Meta:
        verbose_name = lang_text_lazy("Профиль сотрудника", "Қызметкер профилі")
        verbose_name_plural = lang_text_lazy("Профили сотрудников", "Қызметкер профильдері")

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username
