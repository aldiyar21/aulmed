from __future__ import annotations

from pathlib import Path

from django import forms
from django.conf import settings
from django.forms import inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.documents.models import MedicalDocument, PatientFile, Prescription, PrescriptionItem

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}


class MedicalDocumentForm(forms.ModelForm):
    class Meta:
        model = MedicalDocument
        fields = ["patient", "consultation", "encounter", "referral", "document_type", "title", "content", "status", "valid_until"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
            "valid_until": forms.DateInput(attrs={"type": "date"}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "consultation", "status", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    fields=["medication_name", "dosage", "frequency", "duration", "instructions"],
    extra=2,
    can_delete=True,
)


class PatientFileForm(forms.ModelForm):
    class Meta:
        model = PatientFile
        fields = ["patient", "related_consultation", "result_type", "title", "description", "file", "result_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "result_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            raise forms.ValidationError(_("Unsupported file extension."))
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size:
            raise forms.ValidationError(_("File is too large."))
        return uploaded_file

    def clean_result_date(self):
        value = self.cleaned_data["result_date"]
        if value > timezone.localdate():
            raise forms.ValidationError(_("Result date cannot be in the future."))
        return value
