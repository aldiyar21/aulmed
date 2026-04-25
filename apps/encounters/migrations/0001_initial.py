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
            name="Encounter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("encounter_type", models.CharField(choices=[("clinic", "Прием в учреждении"), ("home", "Выезд на дом"), ("preventive", "Профилактика"), ("consult", "Консультация"), ("other", "Другое")], max_length=32, verbose_name="Тип обращения")),
                ("encounter_date", models.DateField(db_index=True, verbose_name="Дата обращения")),
                ("reason_for_visit", models.TextField(verbose_name="Причина обращения")),
                ("diagnosis_text", models.TextField(blank=True, verbose_name="Диагноз")),
                ("services_provided", models.TextField(blank=True, verbose_name="Оказанные услуги")),
                ("result_type", models.CharField(choices=[("treatment", "Лечение"), ("observation", "Наблюдение"), ("referral", "Направление"), ("hospitalization", "Госпитализация"), ("completed", "Завершено")], max_length=32, verbose_name="Результат")),
                ("next_visit_date", models.DateField(blank=True, null=True, verbose_name="Дата следующего визита")),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                ("clinician", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="encounters", to="accounts.employeeprofile", verbose_name="Сотрудник")),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="encounters", to="facilities.facility", verbose_name="Учреждение")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="encounters", to="patients.patient", verbose_name="Пациент")),
            ],
            options={"ordering": ["-encounter_date", "-created_at"], "verbose_name": "Обращение", "verbose_name_plural": "Обращения"},
        ),
    ]
