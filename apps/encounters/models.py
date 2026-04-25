from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class Encounter(TimeStampedModel):
    ENCOUNTER_TYPES = [
        ("clinic", lang_text_lazy("Приём в учреждении", "Ұйымдағы қабылдау")),
        ("home", lang_text_lazy("Выезд на дом", "Үйге бару")),
        ("preventive", lang_text_lazy("Профилактика", "Профилактика")),
        ("consult", lang_text_lazy("Консультация", "Консультация")),
        ("other", lang_text_lazy("Другое", "Басқа")),
    ]
    RESULT_TYPES = [
        ("treatment", lang_text_lazy("Лечение", "Емдеу")),
        ("observation", lang_text_lazy("Наблюдение", "Бақылау")),
        ("referral", lang_text_lazy("Направление", "Жолдама")),
        ("hospitalization", lang_text_lazy("Госпитализация", "Ауруханаға жатқызу")),
        ("completed", lang_text_lazy("Завершено", "Аяқталды")),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name=lang_text_lazy("Учреждение", "Ұйым"),
    )
    clinician = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name=lang_text_lazy("Сотрудник", "Қызметкер"),
    )
    encounter_type = models.CharField(max_length=32, choices=ENCOUNTER_TYPES, verbose_name=lang_text_lazy("Тип обращения", "Қабылдау түрі"))
    encounter_date = models.DateField(db_index=True, verbose_name=lang_text_lazy("Дата обращения", "Қабылдау күні"))
    reason_for_visit = models.TextField(verbose_name=lang_text_lazy("Причина обращения", "Жүгіну себебі"))
    diagnosis_text = models.TextField(blank=True, verbose_name=lang_text_lazy("Диагноз", "Диагноз"))
    services_provided = models.TextField(blank=True, verbose_name=lang_text_lazy("Оказанные услуги", "Көрсетілген қызметтер"))
    result_type = models.CharField(max_length=32, choices=RESULT_TYPES, verbose_name=lang_text_lazy("Результат", "Нәтиже"))
    next_visit_date = models.DateField(blank=True, null=True, verbose_name=lang_text_lazy("Дата следующего визита", "Келесі бару күні"))
    notes = models.TextField(blank=True, verbose_name=lang_text_lazy("Примечания", "Ескертпелер"))

    class Meta:
        ordering = ["-encounter_date", "-created_at"]
        verbose_name = lang_text_lazy("Обращение", "Қабылдау")
        verbose_name_plural = lang_text_lazy("Обращения", "Қабылдаулар")

    def __str__(self) -> str:
        return f"{self.patient} - {self.encounter_date}"
