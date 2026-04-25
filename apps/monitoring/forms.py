from __future__ import annotations

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.monitoring.models import VitalReading


class VitalReadingForm(forms.ModelForm):
    class Meta:
        model = VitalReading
        fields = [
            "recorded_at",
            "systolic_bp",
            "diastolic_bp",
            "pulse",
            "temperature",
            "spo2",
            "glucose",
            "weight",
            "comment",
        ]
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_recorded_at(self):
        value = self.cleaned_data["recorded_at"]
        if value > timezone.now() + timezone.timedelta(hours=2):
            raise forms.ValidationError(_("Recorded time is too far in the future."))
        return value

    def clean(self):
        cleaned_data = super().clean()
        ranges = {
            "systolic_bp": (50, 300),
            "diastolic_bp": (30, 200),
            "pulse": (20, 250),
            "temperature": (30, 45),
            "spo2": (50, 100),
            "glucose": (1, 50),
            "weight": (1, 500),
        }
        for field, (min_value, max_value) in ranges.items():
            value = cleaned_data.get(field)
            if value is not None and not (min_value <= value <= max_value):
                self.add_error(field, _("Value is outside the allowed range."))
        return cleaned_data
