from django.db import models

from apps.core.models import TimeStampedModel


class Referral(TimeStampedModel):
    PRIORITY_CHOICES = [
        ("low", "Низкий"),
        ("medium", "Средний"),
        ("high", "Высокий"),
        ("urgent", "Срочно"),
    ]
    STATUS_CHOICES = [
        ("created", "Создано"),
        ("accepted", "Принято"),
        ("completed", "Завершено"),
        ("no_show", "Не явился"),
        ("cancelled", "Отменено"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="referrals",
        verbose_name="Пациент",
    )
    source_encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referrals",
        verbose_name="Исходное обращение",
    )
    created_by = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="created_referrals",
        verbose_name="Создал",
    )
    destination_org = models.CharField(max_length=255, verbose_name="Организация назначения")
    destination_specialist = models.CharField(max_length=255, verbose_name="Специалист")
    reason = models.TextField(verbose_name="Причина")
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium", verbose_name="Приоритет")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="created", db_index=True)
    referral_date = models.DateField(verbose_name="Дата направления")
    result_note = models.TextField(blank=True, verbose_name="Результат")

    class Meta:
        ordering = ["-referral_date"]
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
