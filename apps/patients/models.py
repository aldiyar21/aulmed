from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel


class Patient(SoftDeleteModel):
    SEX_CHOICES = [("male", "Мужской"), ("female", "Женский")]
    SOCIAL_CATEGORY_CHOICES = [
        ("general", "Общая"),
        ("child", "Ребенок"),
        ("pregnant", "Беременная"),
        ("elderly", "Пожилой"),
        ("disabled", "Лицо с инвалидностью"),
    ]
    RISK_LEVEL_CHOICES = [("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий")]

    last_name = models.CharField(max_length=150, db_index=True, verbose_name="Фамилия")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    iin = models.CharField(max_length=12, unique=True, blank=True, null=True, db_index=True, verbose_name="ИИН")
    birth_date = models.DateField(verbose_name="Дата рождения")
    sex = models.CharField(max_length=16, choices=SEX_CHOICES, verbose_name="Пол")
    phone = models.CharField(max_length=32, blank=True, db_index=True, verbose_name="Телефон")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    settlement_name = models.CharField(max_length=255, verbose_name="Населенный пункт")
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="patients",
        verbose_name="Учреждение",
    )
    patient_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile",
        verbose_name="Пользователь пациента",
    )
    social_category = models.CharField(
        max_length=32,
        choices=SOCIAL_CATEGORY_CHOICES,
        default="general",
        verbose_name="Социальная категория",
    )
    risk_level = models.CharField(
        max_length=16,
        choices=RISK_LEVEL_CHOICES,
        default="low",
        verbose_name="Группа риска",
    )
    attachment_date = models.DateField(verbose_name="Дата прикрепления")
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name"]),
            models.Index(fields=["phone"]),
        ]
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"

    def __str__(self) -> str:
        full_name = " ".join(part for part in [self.last_name, self.first_name, self.middle_name] if part)
        return full_name


class PatientCondition(TimeStampedModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="conditions",
        verbose_name="Пациент",
    )
    condition_name = models.CharField(max_length=255, verbose_name="Состояние")
    icd_code = models.CharField(max_length=16, blank=True, verbose_name="Код МКБ")
    is_chronic = models.BooleanField(default=False, verbose_name="Хроническое")
    diagnosed_at = models.DateField(blank=True, null=True, verbose_name="Дата диагностики")
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        ordering = ["condition_name"]
        verbose_name = "Состояние пациента"
        verbose_name_plural = "Состояния пациентов"
