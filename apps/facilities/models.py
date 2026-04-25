from django.db import models

from apps.core.models import TimeStampedModel


class Facility(TimeStampedModel):
    FACILITY_TYPES = [
        ("fap", "ФАП"),
        ("ambulatoria", "Амбулатория"),
        ("clinic", "Поликлиника"),
        ("other", "Другое"),
    ]

    name = models.CharField(max_length=255, verbose_name="Название")
    facility_type = models.CharField(max_length=32, choices=FACILITY_TYPES, verbose_name="Тип")
    region = models.CharField(max_length=255, verbose_name="Регион")
    district = models.CharField(max_length=255, verbose_name="Район")
    settlement_name = models.CharField(max_length=255, verbose_name="Населенный пункт")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone = models.CharField(max_length=32, blank=True, verbose_name="Телефон")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        ordering = ["name"]
        verbose_name = "Учреждение"
        verbose_name_plural = "Учреждения"

    def __str__(self) -> str:
        return self.name
