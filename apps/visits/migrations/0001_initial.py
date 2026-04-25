from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("facilities", "0001_initial"),
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("planned_date", models.DateField(db_index=True, verbose_name="Дата выезда")),
                ("settlement_name", models.CharField(max_length=255, verbose_name="Населенный пункт")),
                ("status", models.CharField(choices=[("planned", "Запланирован"), ("completed", "Завершен"), ("cancelled", "Отменен")], default="planned", max_length=16, verbose_name="Статус")),
                ("purpose", models.TextField(verbose_name="Цель")),
                ("route_notes", models.TextField(blank=True, verbose_name="Маршрут")),
                ("result_summary", models.TextField(blank=True, verbose_name="Итог")),
                ("assigned_employee", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="assigned_home_visits", to="accounts.employeeprofile", verbose_name="Ответственный сотрудник")),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="home_visits", to="facilities.facility", verbose_name="Учреждение")),
            ],
            options={"ordering": ["planned_date", "settlement_name"], "verbose_name": "Выезд на дом", "verbose_name_plural": "Выезды на дом"},
        ),
        migrations.CreateModel(
            name="HomeVisitPatient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("outcome", models.CharField(blank=True, max_length=255, verbose_name="Результат")),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                ("home_visit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visit_patients", to="visits.homevisit", verbose_name="Выезд")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="home_visit_links", to="patients.patient", verbose_name="Пациент")),
            ],
            options={"verbose_name": "Пациент выезда", "verbose_name_plural": "Пациенты выезда"},
        ),
        migrations.AlterUniqueTogether(name="homevisitpatient", unique_together={("home_visit", "patient")}),
    ]
