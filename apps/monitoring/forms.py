from __future__ import annotations

from django import forms
from django.utils import timezone

from apps.core.i18n import lang_text_lazy
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
        labels = {
            "recorded_at": lang_text_lazy("Дата и время", "Күні мен уақыты"),
            "systolic_bp": lang_text_lazy("Систолическое давление", "Систолалық қысым"),
            "diastolic_bp": lang_text_lazy("Диастолическое давление", "Диастолалық қысым"),
            "pulse": lang_text_lazy("Пульс", "Пульс"),
            "temperature": lang_text_lazy("Температура", "Температура"),
            "spo2": lang_text_lazy("SpO2", "SpO2"),
            "glucose": lang_text_lazy("Глюкоза", "Глюкоза"),
            "weight": lang_text_lazy("Вес", "Салмақ"),
            "comment": lang_text_lazy("Комментарий", "Түсініктеме"),
        }
        widgets = {
            "recorded_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_recorded_at(self):
        value = self.cleaned_data["recorded_at"]
        if value > timezone.now() + timezone.timedelta(hours=2):
            raise forms.ValidationError(
                lang_text_lazy(
                    "Время измерения слишком далеко в будущем.",
                    "Өлшеу уақыты тым алдағы уақытқа қойылған.",
                )
            )
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
                self.add_error(
                    field,
                    lang_text_lazy(
                        "Значение выходит за допустимый диапазон.",
                        "Мән рұқсат етілген ауқымнан тыс.",
                    ),
                )
        return cleaned_data
