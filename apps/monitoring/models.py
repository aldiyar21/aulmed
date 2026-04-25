from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class VitalReading(TimeStampedModel):
    class Source(models.TextChoices):
        PATIENT_MANUAL = "patient_manual", _("Patient manual")
        DOCTOR_MANUAL = "doctor_manual", _("Doctor manual")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="vital_readings")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="recorded_vital_readings",
    )
    source = models.CharField(max_length=24, choices=Source.choices)
    recorded_at = models.DateTimeField()
    systolic_bp = models.PositiveIntegerField(blank=True, null=True)
    diastolic_bp = models.PositiveIntegerField(blank=True, null=True)
    pulse = models.PositiveIntegerField(blank=True, null=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    spo2 = models.PositiveIntegerField(blank=True, null=True)
    glucose = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-recorded_at", "-created_at"]
