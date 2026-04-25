from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class MedicalDocument(TimeStampedModel):
    class DocumentType(models.TextChoices):
        CERTIFICATE = "certificate", lang_text_lazy("Справка", "Анықтама")
        EXTRACT = "extract", lang_text_lazy("Выписка", "Үзінді")
        RECOMMENDATION = "recommendation", lang_text_lazy("Рекомендация", "Ұсыным")

    class Status(models.TextChoices):
        DRAFT = "draft", lang_text_lazy("Черновик", "Нобай")
        ISSUED = "issued", lang_text_lazy("Выдан", "Берілді")
        CANCELLED = "cancelled", lang_text_lazy("Отменён", "Күші жойылды")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="medical_documents", verbose_name=lang_text_lazy("Пациент", "Пациент"))
    consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
        verbose_name=lang_text_lazy("Консультация", "Консультация"),
    )
    encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
        verbose_name=lang_text_lazy("Обращение", "Қабылдау"),
    )
    referral = models.ForeignKey(
        "referrals.Referral",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="medical_documents",
        verbose_name=lang_text_lazy("Направление", "Жолдама"),
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="medical_documents", verbose_name=lang_text_lazy("Создал", "Жасаған"))
    document_type = models.CharField(max_length=24, choices=DocumentType.choices, verbose_name=lang_text_lazy("Тип документа", "Құжат түрі"))
    number = models.CharField(max_length=32, unique=True, blank=True, verbose_name=lang_text_lazy("Номер", "Нөмір"))
    title = models.CharField(max_length=255, verbose_name=lang_text_lazy("Заголовок", "Тақырып"))
    content = models.TextField(verbose_name=lang_text_lazy("Содержание", "Мазмұны"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, verbose_name=lang_text_lazy("Статус", "Күйі"))
    issued_at = models.DateTimeField(blank=True, null=True, verbose_name=lang_text_lazy("Выдан", "Берілген күні"))
    valid_until = models.DateField(blank=True, null=True, verbose_name=lang_text_lazy("Действует до", "Жарамды мерзімі"))

    class Meta:
        verbose_name = lang_text_lazy("Медицинский документ", "Медициналық құжат")
        verbose_name_plural = lang_text_lazy("Медицинские документы", "Медициналық құжаттар")


class Prescription(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", lang_text_lazy("Черновик", "Нобай")
        ISSUED = "issued", lang_text_lazy("Выдан", "Берілді")
        CANCELLED = "cancelled", lang_text_lazy("Отменён", "Күші жойылды")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="prescriptions", verbose_name=lang_text_lazy("Пациент", "Пациент"))
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="prescriptions", verbose_name=lang_text_lazy("Врач", "Дәрігер"))
    consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prescriptions",
        verbose_name=lang_text_lazy("Консультация", "Консультация"),
    )
    number = models.CharField(max_length=32, unique=True, blank=True, verbose_name=lang_text_lazy("Номер", "Нөмір"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, verbose_name=lang_text_lazy("Статус", "Күйі"))
    issued_at = models.DateTimeField(blank=True, null=True, verbose_name=lang_text_lazy("Выдан", "Берілген күні"))
    notes = models.TextField(blank=True, verbose_name=lang_text_lazy("Примечание", "Ескертпе"))

    class Meta:
        verbose_name = lang_text_lazy("Рецепт", "Рецепт")
        verbose_name_plural = lang_text_lazy("Рецепты", "Рецепттер")


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items", verbose_name=lang_text_lazy("Рецепт", "Рецепт"))
    medication_name = models.CharField(max_length=255, verbose_name=lang_text_lazy("Препарат", "Дәрі атауы"))
    dosage = models.CharField(max_length=255, verbose_name=lang_text_lazy("Дозировка", "Дозасы"))
    frequency = models.CharField(max_length=255, verbose_name=lang_text_lazy("Частота приёма", "Қабылдау жиілігі"))
    duration = models.CharField(max_length=255, verbose_name=lang_text_lazy("Длительность", "Ұзақтығы"))
    instructions = models.TextField(blank=True, verbose_name=lang_text_lazy("Инструкция", "Нұсқаулық"))

    class Meta:
        verbose_name = lang_text_lazy("Позиция рецепта", "Рецепт тармағы")
        verbose_name_plural = lang_text_lazy("Позиции рецепта", "Рецепт тармақтары")


class PatientFile(TimeStampedModel):
    class ResultType(models.TextChoices):
        LAB = "lab", lang_text_lazy("Лаборатория", "Зертхана")
        IMAGING = "imaging", lang_text_lazy("Снимок", "Бейнелеу нәтижесі")
        DOCUMENT = "document", lang_text_lazy("Документ", "Құжат")
        PHOTO = "photo", lang_text_lazy("Фото", "Фото")
        OTHER = "other", lang_text_lazy("Другое", "Басқа")

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="patient_files", verbose_name=lang_text_lazy("Пациент", "Пациент"))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_patient_files", verbose_name=lang_text_lazy("Загрузил", "Жүктеген"))
    related_consultation = models.ForeignKey(
        "telemedicine.OnlineConsultation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="patient_files",
        verbose_name=lang_text_lazy("Связанная консультация", "Байланысты консультация"),
    )
    result_type = models.CharField(max_length=24, choices=ResultType.choices, verbose_name=lang_text_lazy("Тип результата", "Нәтиже түрі"))
    title = models.CharField(max_length=255, verbose_name=lang_text_lazy("Название", "Атауы"))
    description = models.TextField(blank=True, verbose_name=lang_text_lazy("Описание", "Сипаттама"))
    file = models.FileField(upload_to="patient_files/%Y/%m/", verbose_name=lang_text_lazy("Файл", "Файл"))
    result_date = models.DateField(verbose_name=lang_text_lazy("Дата результата", "Нәтиже күні"))

    class Meta:
        verbose_name = lang_text_lazy("Файл пациента", "Пациент файлы")
        verbose_name_plural = lang_text_lazy("Файлы пациента", "Пациент файлдары")
