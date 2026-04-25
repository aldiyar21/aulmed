from django.db import models

from apps.core.models import TimeStampedModel


class HomeVisit(TimeStampedModel):
    STATUS_CHOICES = [
        ("planned", "Запланирован"),
        ("completed", "Завершен"),
        ("cancelled", "Отменен"),
    ]

    planned_date = models.DateField(db_index=True, verbose_name="Дата выезда")
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="home_visits",
        verbose_name="Учреждение",
    )
    assigned_employee = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="assigned_home_visits",
        verbose_name="Ответственный сотрудник",
    )
    settlement_name = models.CharField(max_length=255, verbose_name="Населенный пункт")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planned", verbose_name="Статус")
    purpose = models.TextField(verbose_name="Цель")
    route_notes = models.TextField(blank=True, verbose_name="Маршрут")
    result_summary = models.TextField(blank=True, verbose_name="Итог")

    class Meta:
        ordering = ["planned_date", "settlement_name"]
        verbose_name = "Выезд на дом"
        verbose_name_plural = "Выезды на дом"


class HomeVisitPatient(models.Model):
    home_visit = models.ForeignKey(
        HomeVisit,
        on_delete=models.CASCADE,
        related_name="visit_patients",
        verbose_name="Выезд",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="home_visit_links",
        verbose_name="Пациент",
    )
    outcome = models.CharField(max_length=255, blank=True, verbose_name="Результат")
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        unique_together = ("home_visit", "patient")
        verbose_name = "Пациент выезда"
        verbose_name_plural = "Пациенты выезда"
