from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from apps.core.i18n import lang_text_lazy
from apps.telemedicine.models import OnlineConsultation, Teleconsilium


class ConsultationCompletionForm(ModelForm):
    anamnesis = forms.CharField(
        required=False,
        label=lang_text_lazy("Анамнез", "Анамнез"),
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    diagnosis_text = forms.CharField(
        required=False,
        label=lang_text_lazy("Диагноз", "Диагноз"),
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    treatment_plan = forms.CharField(
        required=False,
        label=lang_text_lazy("План лечения", "Емдеу жоспары"),
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    doctor_recommendations = forms.CharField(
        required=False,
        label=lang_text_lazy("Рекомендации врача", "Дәрігер ұсынымдары"),
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    follow_up_required = forms.BooleanField(
        required=False,
        label=lang_text_lazy("Нужно повторное наблюдение", "Қайта бақылау қажет"),
    )
    follow_up_date = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата повторного наблюдения", "Қайта бақылау күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )

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
    status = forms.ChoiceField(
        required=False,
        choices=[("", _("All"))] + list(OnlineConsultation.Status.choices),
        label=lang_text_lazy("Статус", "Күйі"),
    )
    date_from = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата с", "Басталу күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    date_to = forms.DateField(
        required=False,
        label=lang_text_lazy("Дата по", "Аяқталу күні"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )


class TeleconsiliumForm(ModelForm):
    invited_doctors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(employee_profile__role_code="clinician", is_active=True),
        required=False,
        label=lang_text_lazy("Приглашённые врачи", "Шақырылған дәрігерлер"),
    )

    class Meta:
        model = Teleconsilium
        fields = ["patient", "facility", "topic", "description", "status", "scheduled_at", "invited_doctors"]
        labels = {
            "patient": lang_text_lazy("Пациент", "Пациент"),
            "facility": lang_text_lazy("Учреждение", "Ұйым"),
            "topic": lang_text_lazy("Тема", "Тақырып"),
            "description": lang_text_lazy("Описание", "Сипаттама"),
            "status": lang_text_lazy("Статус", "Күйі"),
            "scheduled_at": lang_text_lazy("Дата и время", "Күні мен уақыты"),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class TeleconsiliumCompleteForm(ModelForm):
    class Meta:
        model = Teleconsilium
        fields = ["conclusion", "status"]
        labels = {
            "conclusion": lang_text_lazy("Заключение", "Қорытынды"),
            "status": lang_text_lazy("Статус", "Күйі"),
        }
        widgets = {"conclusion": forms.Textarea(attrs={"rows": 4})}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("status") == Teleconsilium.Status.COMPLETED and not cleaned_data.get("conclusion"):
            self.add_error("conclusion", _("Conclusion is required."))
        return cleaned_data
