from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class MedicalDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        CERTIFICATE = "certificate", _("Certificate")
        EXTRACT = "extract", _("Extract")
        RECOMMENDATION = "recommendation", _("Recommendation")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ISSUED = "issued", _("Issued")
        CANCELLED = "cancelled", _("Cancelled")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="medical_documents")
    consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
    )
    encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
    )
    referral = models.ForeignKey(
        "referrals.Referral",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="medical_documents")
    document_type = models.CharField(max_length=24, choices=DocumentType.choices)
    number = models.CharField(max_length=32, unique=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateTimeField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)


class Prescription(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ISSUED = "issued", _("Issued")
        CANCELLED = "cancelled", _("Cancelled")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="prescriptions")
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prescriptions")
    consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prescriptions",
    )
    number = models.CharField(max_length=32, unique=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    issued_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    frequency = models.CharField(max_length=255)
    duration = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)


class PatientFile(TimeStampedModel):
    class ResultType(models.TextChoices):
        LAB = "lab", _("Lab")
        IMAGING = "imaging", _("Imaging")
        DOCUMENT = "document", _("Document")
        PHOTO = "photo", _("Photo")
        OTHER = "other", _("Other")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="patient_files")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_patient_files")
    related_consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="patient_files",
    )
    result_type = models.CharField(max_length=24, choices=ResultType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="patient_files/%Y/%m/")
    result_date = models.DateField()
