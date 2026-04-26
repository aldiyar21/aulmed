from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.appointments.models import Appointment
from apps.core.forms import html5_date_input, html5_datetime_input
from apps.core.i18n import lang_text_lazy
from apps.facilities.models import Facility


class AppointmentPatientForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["facility", "appointment_type", "requested_datetime", "reason"]
        labels = {
            "facility": lang_text_lazy("Учреждение", "Ұйым"),
            "appointment_type": lang_text_lazy("Тип записи", "Жазылу түрі"),
            "requested_datetime": lang_text_lazy("Желаемое время", "Қажетті уақыт"),
            "reason": lang_text_lazy("Причина обращения", "Жүгіну себебі"),
        }
        widgets = {
            "requested_datetime": html5_datetime_input(),
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
        label=lang_text_lazy("Врач", "Дәрігер"),
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
        labels = {
            "status": lang_text_lazy("Статус", "Күйі"),
            "scheduled_datetime": lang_text_lazy("Назначенное время", "Жоспарланған уақыт"),
            "duration_minutes": lang_text_lazy("Длительность (минуты)", "Ұзақтығы (минут)"),
            "appointment_type": lang_text_lazy("Тип записи", "Жазылу түрі"),
            "reason": lang_text_lazy("Причина обращения", "Жүгіну себебі"),
            "cancellation_reason": lang_text_lazy("Причина отмены", "Бас тарту себебі"),
        }
        widgets = {
            "scheduled_datetime": html5_datetime_input(),
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
        label=lang_text_lazy("Статус", "Күйі"),
    )
    appointment_type = forms.ChoiceField(
        required=False,
        choices=[("", _("All"))] + list(Appointment.AppointmentType.choices),
        label=lang_text_lazy("Тип записи", "Жазылу түрі"),
    )
    date_from = forms.DateField(
        required=False,
        widget=html5_date_input(),
        label=lang_text_lazy("С", "Бастап"),
    )
    date_to = forms.DateField(
        required=False,
        widget=html5_date_input(),
        label=lang_text_lazy("По", "Дейін"),
    )
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(is_active=True),
        required=False,
        label=lang_text_lazy("Учреждение", "Ұйым"),
    )
