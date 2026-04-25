from django.db import models

from apps.core.models import TimeStampedModel


class Encounter(TimeStampedModel):
    ENCOUNTER_TYPES = [
        ("clinic", "Прием в учреждении"),
        ("home", "Выезд на дом"),
        ("preventive", "Профилактика"),
        ("consult", "Консультация"),
        ("other", "Другое"),
    ]
    RESULT_TYPES = [
        ("treatment", "Лечение"),
        ("observation", "Наблюдение"),
        ("referral", "Направление"),
        ("hospitalization", "Госпитализация"),
        ("completed", "Завершено"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name="Пациент",
    )
    facility = models.ForeignKey(
        "facilities.Facility",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name="Учреждение",
    )
    clinician = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="encounters",
        verbose_name="Сотрудник",
    )
    encounter_type = models.CharField(max_length=32, choices=ENCOUNTER_TYPES, verbose_name="Тип обращения")
    encounter_date = models.DateField(db_index=True, verbose_name="Дата обращения")
    reason_for_visit = models.TextField(verbose_name="Причина обращения")
    diagnosis_text = models.TextField(blank=True, verbose_name="Диагноз")
    services_provided = models.TextField(blank=True, verbose_name="Оказанные услуги")
    result_type = models.CharField(max_length=32, choices=RESULT_TYPES, verbose_name="Результат")
    next_visit_date = models.DateField(blank=True, null=True, verbose_name="Дата следующего визита")
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        ordering = ["-encounter_date", "-created_at"]
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"

    def __str__(self) -> str:
        return f"{self.patient} - {self.encounter_date}"
