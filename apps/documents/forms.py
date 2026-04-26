from __future__ import annotations

from pathlib import Path

from django import forms
from django.conf import settings
from django.forms import inlineformset_factory
from django.utils import timezone

from apps.core.forms import html5_date_input
from apps.core.i18n import lang_text_lazy
from apps.documents.models import MedicalDocument, PatientFile, Prescription, PrescriptionItem
from apps.encounters.models import Encounter
from apps.patients.models import Patient
from apps.referrals.models import Referral
from apps.telemedicine.models import OnlineConsultation

ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}


class MedicalDocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patient = None
        patient_value = self.data.get("patient") or self.initial.get("patient")
        if patient_value:
            patient = Patient.objects.filter(pk=patient_value).first()
        elif self.instance.pk:
            patient = self.instance.patient

        if patient:
            self.fields["consultation"].queryset = OnlineConsultation.objects.filter(patient=patient)
            self.fields["encounter"].queryset = Encounter.objects.filter(patient=patient)
            self.fields["referral"].queryset = Referral.objects.filter(patient=patient)
        else:
            self.fields["consultation"].queryset = OnlineConsultation.objects.none()
            self.fields["encounter"].queryset = Encounter.objects.none()
            self.fields["referral"].queryset = Referral.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        relations = (
            ("consultation", cleaned_data.get("consultation")),
            ("encounter", cleaned_data.get("encounter")),
            ("referral", cleaned_data.get("referral")),
        )
        for field_name, relation in relations:
            if relation and patient and relation.patient_id != patient.pk:
                self.add_error(
                    field_name,
                    lang_text_lazy(
                        "Можно выбрать только данные выбранного пациента.",
                        "Тек таңдалған пациенттің деректерін таңдауға болады.",
                    ),
                )
        return cleaned_data

    class Meta:
        model = MedicalDocument
        fields = ["patient", "consultation", "encounter", "referral", "document_type", "title", "content", "status", "valid_until"]
        labels = {
            "patient": lang_text_lazy("Пациент", "Пациент"),
            "consultation": lang_text_lazy("Консультация", "Консультация"),
            "encounter": lang_text_lazy("Обращение", "Қабылдау"),
            "referral": lang_text_lazy("Направление", "Жолдама"),
            "document_type": lang_text_lazy("Тип документа", "Құжат түрі"),
            "title": lang_text_lazy("Заголовок", "Тақырып"),
            "content": lang_text_lazy("Содержание", "Мазмұны"),
            "status": lang_text_lazy("Статус", "Күйі"),
            "valid_until": lang_text_lazy("Действует до", "Жарамды мерзімі"),
        }
        widgets = {
            "content": forms.Textarea(attrs={"rows": 8}),
            "valid_until": html5_date_input(),
        }


class PrescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patient = None
        patient_value = self.data.get("patient") or self.initial.get("patient")
        if patient_value:
            patient = Patient.objects.filter(pk=patient_value).first()
        elif self.instance.pk:
            patient = self.instance.patient

        if patient:
            self.fields["consultation"].queryset = OnlineConsultation.objects.filter(patient=patient)
        else:
            self.fields["consultation"].queryset = OnlineConsultation.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        consultation = cleaned_data.get("consultation")
        if consultation and patient and consultation.patient_id != patient.pk:
            self.add_error(
                "consultation",
                lang_text_lazy(
                    "Можно выбрать только консультацию выбранного пациента.",
                    "Тек таңдалған пациенттің консультациясын таңдауға болады.",
                ),
            )
        return cleaned_data

    class Meta:
        model = Prescription
        fields = ["patient", "consultation", "status", "notes"]
        labels = {
            "patient": lang_text_lazy("Пациент", "Пациент"),
            "consultation": lang_text_lazy("Консультация", "Консультация"),
            "status": lang_text_lazy("Статус", "Күйі"),
            "notes": lang_text_lazy("Примечание", "Ескертпе"),
        }
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ["medication_name", "dosage", "frequency", "duration", "instructions"]
        labels = {
            "medication_name": lang_text_lazy("Препарат", "Дәрі атауы"),
            "dosage": lang_text_lazy("Дозировка", "Дозасы"),
            "frequency": lang_text_lazy("Частота приёма", "Қабылдау жиілігі"),
            "duration": lang_text_lazy("Длительность", "Ұзақтығы"),
            "instructions": lang_text_lazy("Инструкция", "Нұсқаулық"),
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    fields=["medication_name", "dosage", "frequency", "duration", "instructions"],
    extra=2,
    can_delete=True,
)


class PatientFileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patient = None
        patient_value = self.data.get("patient") or self.initial.get("patient")
        if patient_value:
            patient = Patient.objects.filter(pk=patient_value).first()
        elif self.instance.pk:
            patient = self.instance.patient

        if patient:
            self.fields["related_consultation"].queryset = OnlineConsultation.objects.filter(patient=patient)
        else:
            self.fields["related_consultation"].queryset = OnlineConsultation.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        consultation = cleaned_data.get("related_consultation")
        if consultation and patient and consultation.patient_id != patient.pk:
            self.add_error(
                "related_consultation",
                lang_text_lazy(
                    "Можно выбрать только консультацию выбранного пациента.",
                    "Тек таңдалған пациенттің консультациясын таңдауға болады.",
                ),
            )
        return cleaned_data

    class Meta:
        model = PatientFile
        fields = ["patient", "related_consultation", "result_type", "title", "description", "file", "result_date"]
        labels = {
            "patient": lang_text_lazy("Пациент", "Пациент"),
            "related_consultation": lang_text_lazy("Связанная консультация", "Байланысты консультация"),
            "result_type": lang_text_lazy("Тип результата", "Нәтиже түрі"),
            "title": lang_text_lazy("Название", "Атауы"),
            "description": lang_text_lazy("Описание", "Сипаттама"),
            "file": lang_text_lazy("Файл", "Файл"),
            "result_date": lang_text_lazy("Дата результата", "Нәтиже күні"),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "result_date": html5_date_input(),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        suffix = Path(uploaded_file.name).suffix.lower()
        if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
            raise forms.ValidationError(
                lang_text_lazy(
                    "Неподдерживаемое расширение файла.",
                    "Файл кеңейтімі қолдау көрсетілмейді.",
                )
            )
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if uploaded_file.size > max_size:
            raise forms.ValidationError(
                lang_text_lazy("Файл слишком большой.", "Файл өлшемі тым үлкен.")
            )
        return uploaded_file

    def clean_result_date(self):
        value = self.cleaned_data["result_date"]
        if value > timezone.localdate():
            raise forms.ValidationError(
                lang_text_lazy(
                    "Дата результата не может быть в будущем.",
                    "Нәтиже күні болашақта болмауы керек.",
                )
            )
        return value
