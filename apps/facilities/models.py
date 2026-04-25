from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class Facility(TimeStampedModel):
    FACILITY_TYPES = [
        ("fap", lang_text_lazy("ФАП", "ФАП")),
        ("ambulatoria", lang_text_lazy("Амбулатория", "Амбулатория")),
        ("clinic", lang_text_lazy("Поликлиника", "Емхана")),
        ("other", lang_text_lazy("Другое", "Басқа")),
    ]

    name = models.CharField(max_length=255, verbose_name=lang_text_lazy("Название", "Атауы"))
    facility_type = models.CharField(max_length=32, choices=FACILITY_TYPES, verbose_name=lang_text_lazy("Тип", "Түрі"))
    region = models.CharField(max_length=255, verbose_name=lang_text_lazy("Регион", "Өңір"))
    district = models.CharField(max_length=255, verbose_name=lang_text_lazy("Район", "Аудан"))
    settlement_name = models.CharField(max_length=255, verbose_name=lang_text_lazy("Населенный пункт", "Елді мекен"))
    address = models.CharField(max_length=255, verbose_name=lang_text_lazy("Адрес", "Мекенжай"))
    phone = models.CharField(max_length=32, blank=True, verbose_name=lang_text_lazy("Телефон", "Телефон"))
    is_active = models.BooleanField(default=True, verbose_name=lang_text_lazy("Активно", "Белсенді"))

    class Meta:
        ordering = ["name"]
        verbose_name = lang_text_lazy("Учреждение", "Ұйым")
        verbose_name_plural = lang_text_lazy("Учреждения", "Ұйымдар")

    def __str__(self) -> str:
        return self.name
