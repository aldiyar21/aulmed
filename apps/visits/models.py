from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class HomeVisit(TimeStampedModel):
    STATUS_CHOICES = [
        ("planned", lang_text_lazy("Запланирован", "Жоспарланған")),
        ("completed", lang_text_lazy("Завершен", "Аяқталған")),
        ("cancelled", lang_text_lazy("Отменен", "Бас тартылған")),
    ]

    planned_date = models.DateField(db_index=True, verbose_name=lang_text_lazy("Дата выезда", "Шығу күні"))
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="home_visits",
        verbose_name=lang_text_lazy("Учреждение", "Ұйым"),
    )
    assigned_employee = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="assigned_home_visits",
        verbose_name=lang_text_lazy("Ответственный сотрудник", "Жауапты қызметкер"),
    )
    settlement_name = models.CharField(max_length=255, verbose_name=lang_text_lazy("Населенный пункт", "Елді мекен"))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planned", verbose_name=lang_text_lazy("Статус", "Күйі"))
    purpose = models.TextField(verbose_name=lang_text_lazy("Цель", "Мақсаты"))
    route_notes = models.TextField(blank=True, verbose_name=lang_text_lazy("Маршрут", "Бағыт"))
    result_summary = models.TextField(blank=True, verbose_name=lang_text_lazy("Итог", "Қорытынды"))

    class Meta:
        ordering = ["planned_date", "settlement_name"]
        verbose_name = lang_text_lazy("Выезд на дом", "Үйге бару")
        verbose_name_plural = lang_text_lazy("Выезды на дом", "Үйге барулар")


class HomeVisitPatient(models.Model):
    home_visit = models.ForeignKey(
        HomeVisit,
        on_delete=models.CASCADE,
        related_name="visit_patients",
        verbose_name=lang_text_lazy("Выезд", "Шығу"),
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="home_visit_links",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    outcome = models.CharField(max_length=255, blank=True, verbose_name=lang_text_lazy("Результат", "Нәтиже"))
    notes = models.TextField(blank=True, verbose_name=lang_text_lazy("Примечания", "Ескертпелер"))

    class Meta:
        unique_together = ("home_visit", "patient")
        verbose_name = lang_text_lazy("Пациент выезда", "Шығу пациенті")
        verbose_name_plural = lang_text_lazy("Пациенты выезда", "Шығу пациенттері")
