from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


def generate_room_name(prefix: str | None = None) -> str:
    prefix = prefix or settings.JITSI_ROOM_PREFIX
    return f"{prefix}-{uuid.uuid4().hex}"


class OnlineConsultation(TimeStampedModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", lang_text_lazy("Запрошено", "Сұралған")
        SCHEDULED = "scheduled", lang_text_lazy("Назначено", "Жоспарланған")
        WAITING_PATIENT = "waiting_patient", lang_text_lazy("Ожидание пациента", "Пациентті күту")
        WAITING_DOCTOR = "waiting_doctor", lang_text_lazy("Ожидание врача", "Дәрігерді күту")
        IN_PROGRESS = "in_progress", lang_text_lazy("Идёт", "Өтіп жатыр")
        COMPLETED = "completed", lang_text_lazy("Завершено", "Аяқталды")
        CANCELLED = "cancelled", lang_text_lazy("Отменено", "Бас тартылды")

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="online_consultation",
        verbose_name=lang_text_lazy("Запись", "Жазылу"),
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="online_consultations",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="online_consultations",
        verbose_name=lang_text_lazy("Врач", "Дәрігер"),
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="online_consultations",
        verbose_name=lang_text_lazy("Учреждение", "Ұйым"),
    )
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True,
        verbose_name=lang_text_lazy("Статус", "Күйі"),
    )
    scheduled_start = models.DateTimeField(verbose_name=lang_text_lazy("Плановое начало", "Жоспарланған басталу"))
    scheduled_end = models.DateTimeField(verbose_name=lang_text_lazy("Плановое завершение", "Жоспарланған аяқталу"))
    actual_started_at = models.DateTimeField(blank=True, null=True, verbose_name=lang_text_lazy("Фактическое начало", "Нақты басталу"))
    actual_ended_at = models.DateTimeField(blank=True, null=True, verbose_name=lang_text_lazy("Фактическое завершение", "Нақты аяқталу"))
    complaint = models.TextField(blank=True, verbose_name=lang_text_lazy("Жалоба", "Шағым"))
    anamnesis = models.TextField(blank=True, verbose_name=lang_text_lazy("Анамнез", "Анамнез"))
    doctor_recommendations = models.TextField(blank=True, verbose_name=lang_text_lazy("Рекомендации врача", "Дәрігер ұсынымдары"))
    diagnosis_text = models.TextField(blank=True, verbose_name=lang_text_lazy("Диагноз", "Диагноз"))
    treatment_plan = models.TextField(blank=True, verbose_name=lang_text_lazy("План лечения", "Емдеу жоспары"))
    follow_up_required = models.BooleanField(default=False, verbose_name=lang_text_lazy("Нужно повторное наблюдение", "Қайта бақылау қажет"))
    follow_up_date = models.DateField(blank=True, null=True, verbose_name=lang_text_lazy("Дата повторного наблюдения", "Қайта бақылау күні"))
    jitsi_domain = models.CharField(max_length=255, default=settings.JITSI_DOMAIN, verbose_name=lang_text_lazy("Домен Jitsi", "Jitsi домені"))
    jitsi_room_name = models.CharField(max_length=255, default=generate_room_name, unique=True, verbose_name=lang_text_lazy("Комната Jitsi", "Jitsi бөлмесі"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_online_consultations",
        verbose_name=lang_text_lazy("Создал", "Жасаған"),
    )

    class Meta:
        ordering = ["-scheduled_start", "-created_at"]
        verbose_name = lang_text_lazy("Онлайн-консультация", "Онлайн консультация")
        verbose_name_plural = lang_text_lazy("Онлайн-консультации", "Онлайн консультациялар")

    @property
    def jitsi_room_url(self) -> str:
        return f"https://{self.jitsi_domain}/{self.jitsi_room_name}"

    def __str__(self) -> str:
        return f"{self.patient} / {self.scheduled_start:%Y-%m-%d %H:%M}"


class Teleconsilium(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", lang_text_lazy("Черновик", "Нобай")
        SCHEDULED = "scheduled", lang_text_lazy("Назначено", "Жоспарланған")
        COMPLETED = "completed", lang_text_lazy("Завершено", "Аяқталды")
        CANCELLED = "cancelled", lang_text_lazy("Отменено", "Бас тартылды")

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="teleconsiliums",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    primary_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="primary_teleconsiliums",
        verbose_name=lang_text_lazy("Основной врач", "Негізгі дәрігер"),
    )
    invited_doctors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="invited_teleconsiliums",
        blank=True,
        verbose_name=lang_text_lazy("Приглашённые врачи", "Шақырылған дәрігерлер"),
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="teleconsiliums",
        verbose_name=lang_text_lazy("Учреждение", "Ұйым"),
    )
    topic = models.CharField(max_length=255, verbose_name=lang_text_lazy("Тема", "Тақырып"))
    description = models.TextField(verbose_name=lang_text_lazy("Описание", "Сипаттама"))
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True, verbose_name=lang_text_lazy("Статус", "Күйі"))
    scheduled_at = models.DateTimeField(verbose_name=lang_text_lazy("Дата и время", "Күні мен уақыты"))
    conclusion = models.TextField(blank=True, verbose_name=lang_text_lazy("Заключение", "Қорытынды"))
    jitsi_domain = models.CharField(max_length=255, default=settings.JITSI_DOMAIN, verbose_name=lang_text_lazy("Домен Jitsi", "Jitsi домені"))
    jitsi_room_name = models.CharField(max_length=255, default=generate_room_name, unique=True, verbose_name=lang_text_lazy("Комната Jitsi", "Jitsi бөлмесі"))

    class Meta:
        ordering = ["-scheduled_at", "-created_at"]
        verbose_name = lang_text_lazy("Телеконсилиум", "Телеконсилиум")
        verbose_name_plural = lang_text_lazy("Телеконсилиумы", "Телеконсилиумдар")

    @property
    def jitsi_room_url(self) -> str:
        return f"https://{self.jitsi_domain}/{self.jitsi_room_name}"


class PatientConsent(TimeStampedModel):
    class ConsentType(models.TextChoices):
        TELEMEDICINE = "telemedicine", lang_text_lazy("Телемедицина", "Телемедицина")
        DATA_PROCESSING = "data_processing", lang_text_lazy("Обработка данных", "Деректерді өңдеу")

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="consents",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    consultation = models.ForeignKey(
        OnlineConsultation,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="consents",
        verbose_name=lang_text_lazy("Консультация", "Консультация"),
    )
    consent_type = models.CharField(max_length=32, choices=ConsentType.choices, verbose_name=lang_text_lazy("Тип согласия", "Келісім түрі"))
    accepted_at = models.DateTimeField(verbose_name=lang_text_lazy("Принято", "Қабылданды"))
    accepted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="accepted_consents", verbose_name=lang_text_lazy("Подтвердил", "Растаған"))
    text_snapshot = models.TextField(verbose_name=lang_text_lazy("Текст согласия", "Келісім мәтіні"))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=lang_text_lazy("IP-адрес", "IP мекенжайы"))

    class Meta:
        ordering = ["-accepted_at"]
        verbose_name = lang_text_lazy("Согласие пациента", "Пациент келісімі")
        verbose_name_plural = lang_text_lazy("Согласия пациентов", "Пациент келісімдері")
