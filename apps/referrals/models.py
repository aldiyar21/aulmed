from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class Referral(TimeStampedModel):
    PRIORITY_CHOICES = [
        ("low", lang_text_lazy("Низкий", "Төмен")),
        ("medium", lang_text_lazy("Средний", "Орташа")),
        ("high", lang_text_lazy("Высокий", "Жоғары")),
        ("urgent", lang_text_lazy("Срочно", "Шұғыл")),
    ]
    STATUS_CHOICES = [
        ("created", lang_text_lazy("Создано", "Құрылған")),
        ("accepted", lang_text_lazy("Принято", "Қабылданған")),
        ("completed", lang_text_lazy("Завершено", "Аяқталған")),
        ("no_show", lang_text_lazy("Не явился", "Келмеді")),
        ("cancelled", lang_text_lazy("Отменено", "Бас тартылған")),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.PROTECT,
        related_name="referrals",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    source_encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referrals",
        verbose_name=lang_text_lazy("Исходное обращение", "Бастапқы қабылдау"),
    )
    created_by = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="created_referrals",
        verbose_name=lang_text_lazy("Создал", "Құрған"),
    )
    destination_org = models.CharField(max_length=255, verbose_name=lang_text_lazy("Организация назначения", "Жіберілетін ұйым"))
    destination_specialist = models.CharField(max_length=255, verbose_name=lang_text_lazy("Специалист", "Маман"))
    reason = models.TextField(verbose_name=lang_text_lazy("Причина", "Себебі"))
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="medium", verbose_name=lang_text_lazy("Приоритет", "Басымдық"))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="created", db_index=True)
    referral_date = models.DateField(verbose_name=lang_text_lazy("Дата направления", "Жолдама күні"))
    result_note = models.TextField(blank=True, verbose_name=lang_text_lazy("Результат", "Нәтиже"))

    class Meta:
        ordering = ["-referral_date"]
        verbose_name = lang_text_lazy("Направление", "Жолдама")
        verbose_name_plural = lang_text_lazy("Направления", "Жолдамалар")
