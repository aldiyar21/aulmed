from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PreventionEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(choices=[("screening", "Скрининг"), ("chronic_followup", "Диспансерное наблюдение"), ("pregnancy", "Беременность"), ("child_check", "Осмотр ребенка"), ("elderly_check", "Осмотр пожилого"), ("vaccination_other", "Иное профилактическое")], max_length=32, verbose_name="Тип")),
                ("planned_date", models.DateField(db_index=True, verbose_name="Плановая дата")),
                ("completed_date", models.DateField(blank=True, null=True, verbose_name="Дата выполнения")),
                ("status", models.CharField(choices=[("planned", "Запланировано"), ("overdue", "Просрочено"), ("completed", "Выполнено"), ("cancelled", "Отменено")], db_index=True, default="planned", max_length=16)),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                ("assigned_employee", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="prevention_events", to="accounts.employeeprofile", verbose_name="Ответственный")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prevention_events", to="patients.patient", verbose_name="Пациент")),
            ],
            options={"ordering": ["planned_date"], "verbose_name": "Профилактическое мероприятие", "verbose_name_plural": "Профилактические мероприятия"},
        ),
    ]
