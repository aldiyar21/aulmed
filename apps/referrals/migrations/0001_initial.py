from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("encounters", "0001_initial"),
        ("patients", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Referral",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("destination_org", models.CharField(max_length=255, verbose_name="Организация назначения")),
                ("destination_specialist", models.CharField(max_length=255, verbose_name="Специалист")),
                ("reason", models.TextField(verbose_name="Причина")),
                ("priority", models.CharField(choices=[("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий"), ("urgent", "Срочно")], default="medium", max_length=16, verbose_name="Приоритет")),
                ("status", models.CharField(choices=[("created", "Создано"), ("accepted", "Принято"), ("completed", "Завершено"), ("no_show", "Не явился"), ("cancelled", "Отменено")], db_index=True, default="created", max_length=16)),
                ("referral_date", models.DateField(verbose_name="Дата направления")),
                ("result_note", models.TextField(blank=True, verbose_name="Результат")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_referrals", to="accounts.employeeprofile", verbose_name="Создал")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="referrals", to="patients.patient", verbose_name="Пациент")),
                ("source_encounter", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="referrals", to="encounters.encounter", verbose_name="Исходное обращение")),
            ],
            options={"ordering": ["-referral_date"], "verbose_name": "Направление", "verbose_name_plural": "Направления"},
        ),
    ]
