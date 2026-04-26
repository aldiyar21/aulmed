from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SoftDeleteModel


class Appointment(SoftDeleteModel):
    class AppointmentType(models.TextChoices):
        OFFLINE = "offline", _("Offline")
        ONLINE = "online", _("Online")

    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        APPROVED = "approved", _("Approved")
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")
        NO_SHOW = "no_show", _("No show")

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name=_("Patient"),
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name=_("Facility"),
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="doctor_appointments",
        verbose_name=_("Doctor"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_appointments",
        verbose_name=_("Created by"),
    )
    appointment_type = models.CharField(
        max_length=16,
        choices=AppointmentType.choices,
        default=AppointmentType.OFFLINE,
        verbose_name=_("Appointment type"),
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
        verbose_name=_("Status"),
    )
    requested_datetime = models.DateTimeField(verbose_name=_("Requested datetime"))
    scheduled_datetime = models.DateTimeField(blank=True, null=True, verbose_name=_("Scheduled datetime"))
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name=_("Duration (minutes)"))
    reason = models.TextField(verbose_name=_("Reason / complaint"))
    cancellation_reason = models.TextField(blank=True, verbose_name=_("Cancellation reason"))

    class Meta:
        ordering = ["-requested_datetime", "-created_at"]
        verbose_name = _("Appointment")
        verbose_name_plural = _("Appointments")

    def __str__(self) -> str:
        return f"{self.patient} / {self.get_appointment_type_display()} / {self.requested_datetime:%Y-%m-%d %H:%M}"
