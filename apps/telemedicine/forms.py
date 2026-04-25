from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from apps.telemedicine.models import OnlineConsultation, Teleconsilium


class ConsultationCompletionForm(ModelForm):
    class Meta:
        model = OnlineConsultation
        fields = [
            "anamnesis",
            "diagnosis_text",
            "treatment_plan",
            "doctor_recommendations",
            "follow_up_required",
            "follow_up_date",
        ]
        widgets = {
            "anamnesis": forms.Textarea(attrs={"rows": 4}),
            "diagnosis_text": forms.Textarea(attrs={"rows": 4}),
            "treatment_plan": forms.Textarea(attrs={"rows": 4}),
            "doctor_recommendations": forms.Textarea(attrs={"rows": 4}),
            "follow_up_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any(cleaned_data.get(field) for field in ["doctor_recommendations", "treatment_plan", "diagnosis_text"]):
            raise forms.ValidationError(_("Fill at least one conclusion field."))
        if cleaned_data.get("follow_up_required") and not cleaned_data.get("follow_up_date"):
            self.add_error("follow_up_date", _("Choose a follow-up date."))
        return cleaned_data


class ConsultationFilterForm(forms.Form):
    status = forms.ChoiceField(required=False, choices=[("", _("All"))] + list(OnlineConsultation.Status.choices))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))


class TeleconsiliumForm(ModelForm):
    invited_doctors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(employee_profile__role_code="clinician", is_active=True),
        required=False,
    )

    class Meta:
        model = Teleconsilium
        fields = ["patient", "facility", "topic", "description", "status", "scheduled_at", "invited_doctors"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class TeleconsiliumCompleteForm(ModelForm):
    class Meta:
        model = Teleconsilium
        fields = ["conclusion", "status"]
        widgets = {"conclusion": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("status") == Teleconsilium.Status.COMPLETED and not cleaned_data.get("conclusion"):
            self.add_error("conclusion", _("Conclusion is required."))
        return cleaned_data
