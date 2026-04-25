from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.appointments.models import Appointment
from apps.facilities.models import Facility


class AppointmentPatientForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["facility", "appointment_type", "requested_datetime", "reason"]
        widgets = {
            "requested_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_requested_datetime(self):
        value = self.cleaned_data["requested_datetime"]
        if value < timezone.now() - timezone.timedelta(minutes=5):
            raise forms.ValidationError(_("Choose a current or future time."))
        return value


class AppointmentStaffUpdateForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(employee_profile__role_code="clinician", is_active=True),
        required=False,
        label=_("Doctor"),
    )

    class Meta:
        model = Appointment
        fields = [
            "status",
            "doctor",
            "scheduled_datetime",
            "duration_minutes",
            "appointment_type",
            "reason",
            "cancellation_reason",
        ]
        widgets = {
            "scheduled_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reason": forms.Textarea(attrs={"rows": 4}),
            "cancellation_reason": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        scheduled_datetime = cleaned_data.get("scheduled_datetime")
        doctor = cleaned_data.get("doctor")
        if status in {Appointment.Status.APPROVED, Appointment.Status.SCHEDULED}:
            if not scheduled_datetime:
                self.add_error("scheduled_datetime", _("Scheduled time is required."))
            if not doctor:
                self.add_error("doctor", _("Doctor is required."))
        if status == Appointment.Status.CANCELLED and not cleaned_data.get("cancellation_reason"):
            self.add_error("cancellation_reason", _("Please provide a cancellation reason."))
        return cleaned_data


class AppointmentFilterForm(forms.Form):
    status = forms.ChoiceField(
        required=False,
        choices=[("", _("All"))] + list(Appointment.Status.choices),
        label=_("Status"),
    )
    appointment_type = forms.ChoiceField(
        required=False,
        choices=[("", _("All"))] + list(Appointment.AppointmentType.choices),
        label=_("Appointment type"),
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label=_("From"))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}), label=_("To"))
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label=_("Facility"),
    )
