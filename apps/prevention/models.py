from django.db import models

from apps.core.models import TimeStampedModel


class PreventionEvent(TimeStampedModel):
    EVENT_TYPES = [
        ("screening", "Скрининг"),
        ("chronic_followup", "Диспансерное наблюдение"),
        ("pregnancy", "Беременность"),
        ("child_check", "Осмотр ребенка"),
        ("elderly_check", "Осмотр пожилого"),
        ("vaccination_other", "Иное профилактическое"),
    ]
    STATUS_CHOICES = [
        ("planned", "Запланировано"),
        ("overdue", "Просрочено"),
        ("completed", "Выполнено"),
        ("cancelled", "Отменено"),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="prevention_events",
        verbose_name="Пациент",
    )
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES, verbose_name="Тип")
    planned_date = models.DateField(db_index=True, verbose_name="Плановая дата")
    completed_date = models.DateField(blank=True, null=True, verbose_name="Дата выполнения")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planned", db_index=True)
    assigned_employee = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prevention_events",
        verbose_name="Ответственный",
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        ordering = ["planned_date"]
        verbose_name = "Профилактическое мероприятие"
        verbose_name_plural = "Профилактические мероприятия"
