from django.db import models

from apps.core.i18n import lang_text_lazy
from apps.core.models import TimeStampedModel


class PreventionEvent(TimeStampedModel):
    EVENT_TYPES = [
        ("screening", lang_text_lazy("Скрининг", "Скрининг")),
        ("chronic_followup", lang_text_lazy("Диспансерное наблюдение", "Диспансерлік бақылау")),
        ("pregnancy", lang_text_lazy("Беременность", "Жүктілік")),
        ("child_check", lang_text_lazy("Осмотр ребенка", "Баланы қарау")),
        ("elderly_check", lang_text_lazy("Осмотр пожилого", "Егде жастағыны қарау")),
        ("vaccination_other", lang_text_lazy("Иное профилактическое", "Өзге профилактикалық")),
    ]
    STATUS_CHOICES = [
        ("planned", lang_text_lazy("Запланировано", "Жоспарланған")),
        ("overdue", lang_text_lazy("Просрочено", "Мерзімі өткен")),
        ("completed", lang_text_lazy("Выполнено", "Орындалған")),
        ("cancelled", lang_text_lazy("Отменено", "Бас тартылған")),
    ]

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="prevention_events",
        verbose_name=lang_text_lazy("Пациент", "Пациент"),
    )
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES, verbose_name=lang_text_lazy("Тип", "Түрі"))
    planned_date = models.DateField(db_index=True, verbose_name=lang_text_lazy("Плановая дата", "Жоспарланған күн"))
    completed_date = models.DateField(blank=True, null=True, verbose_name=lang_text_lazy("Дата выполнения", "Орындалған күні"))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planned", db_index=True)
    assigned_employee = models.ForeignKey(
        "accounts.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="prevention_events",
        verbose_name=lang_text_lazy("Ответственный", "Жауапты"),
    )
    notes = models.TextField(blank=True, verbose_name=lang_text_lazy("Примечания", "Ескертпелер"))

    class Meta:
        ordering = ["planned_date"]
        verbose_name = lang_text_lazy("Профилактическое мероприятие", "Профилактикалық іс-шара")
        verbose_name_plural = lang_text_lazy("Профилактические мероприятия", "Профилактикалық іс-шаралар")
