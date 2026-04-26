from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class VitalReading(TimeStampedModel):
    class Source(models.TextChoices):
        PATIENT_MANUAL = "patient_manual", lang_text_lazy("Ввод пациента", "Пациент енгізген")
        DOCTOR_MANUAL = "doctor_manual", lang_text_lazy("Ввод врача", "Дәрігер енгізген")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="vital_readings", verbose_name=lang_text_lazy("Пациент", "Пациент"))
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="recorded_vital_readings",
        verbose_name=lang_text_lazy("Кто внёс", "Енгізген адам"),
    )
    source = models.CharField(max_length=24, choices=Source.choices, verbose_name=lang_text_lazy("Источник", "Дерек көзі"))
    recorded_at = models.DateTimeField(verbose_name=lang_text_lazy("Дата и время", "Күні мен уақыты"))
    systolic_bp = models.PositiveIntegerField(blank=True, null=True, verbose_name=lang_text_lazy("Систолическое давление", "Систолалық қысым"))
    diastolic_bp = models.PositiveIntegerField(blank=True, null=True, verbose_name=lang_text_lazy("Диастолическое давление", "Диастолалық қысым"))
    pulse = models.PositiveIntegerField(blank=True, null=True, verbose_name=lang_text_lazy("Пульс", "Пульс"))
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name=lang_text_lazy("Температура", "Температура"))
    spo2 = models.PositiveIntegerField(blank=True, null=True, verbose_name=lang_text_lazy("SpO2", "SpO2"))
    glucose = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=lang_text_lazy("Глюкоза", "Глюкоза"))
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=lang_text_lazy("Вес", "Салмақ"))
    comment = models.TextField(blank=True, verbose_name=lang_text_lazy("Комментарий", "Түсініктеме"))

    class Meta:
        ordering = ["-recorded_at", "-created_at"]
        verbose_name = lang_text_lazy("Показатель здоровья", "Денсаулық көрсеткіші")
        verbose_name_plural = lang_text_lazy("Показатели здоровья", "Денсаулық көрсеткіштері")
