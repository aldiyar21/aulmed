from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


def generate_room_name(prefix: str | None = None) -> str:
    prefix = prefix or settings.JITSI_ROOM_PREFIX
    return f"{prefix}-{uuid.uuid4().hex}"


class OnlineConsultation(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        SCHEDULED = "scheduled", _("Scheduled")
        WAITING_PATIENT = "waiting_patient", _("Waiting patient")
        WAITING_DOCTOR = "waiting_doctor", _("Waiting doctor")
        IN_PROGRESS = "in_progress", _("In progress")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="online_consultation",
    )
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="online_consultations")
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="online_consultations",
    )
    facility = models.ForeignKey("facilities.Facility", on_delete=models.PROTECT, related_name="online_consultations")
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()
    actual_started_at = models.DateTimeField(blank=True, null=True)
    actual_ended_at = models.DateTimeField(blank=True, null=True)
    complaint = models.TextField(blank=True)
    anamnesis = models.TextField(blank=True)
    doctor_recommendations = models.TextField(blank=True)
    diagnosis_text = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(blank=True, null=True)
    jitsi_domain = models.CharField(max_length=255, default=settings.JITSI_DOMAIN)
    jitsi_room_name = models.CharField(max_length=255, default=generate_room_name, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_online_consultations",
    )

    class Meta:
        ordering = ["-scheduled_start", "-created_at"]

    @property
    def jitsi_room_url(self) -> str:
        return f"https://{self.jitsi_domain}/{self.jitsi_room_name}"

    def __str__(self) -> str:
        return f"{self.patient} / {self.scheduled_start:%Y-%m-%d %H:%M}"


class Teleconsilium(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="teleconsiliums")
    primary_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="primary_teleconsiliums",
    )
    invited_doctors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="invited_teleconsiliums",
        blank=True,
    )
    facility = models.ForeignKey("facilities.Facility", on_delete=models.PROTECT, related_name="teleconsiliums")
    topic = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    scheduled_at = models.DateTimeField()
    conclusion = models.TextField(blank=True)
    jitsi_domain = models.CharField(max_length=255, default=settings.JITSI_DOMAIN)
    jitsi_room_name = models.CharField(max_length=255, default=generate_room_name, unique=True)

    class Meta:
        ordering = ["-scheduled_at", "-created_at"]

    @property
    def jitsi_room_url(self) -> str:
        return f"https://{self.jitsi_domain}/{self.jitsi_room_name}"


class PatientConsent(TimeStampedModel):
    class ConsentType(models.TextChoices):
        TELEMEDICINE = "telemedicine", _("Telemedicine")
        DATA_PROCESSING = "data_processing", _("Data processing")

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="consents")
    consultation = models.ForeignKey(
        OnlineConsultation,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="consents",
    )
    consent_type = models.CharField(max_length=32, choices=ConsentType.choices)
    accepted_at = models.DateTimeField()
    accepted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="accepted_consents")
    text_snapshot = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-accepted_at"]
