from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("facilities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("last_name", models.CharField(db_index=True, max_length=150, verbose_name="Фамилия")),
                ("first_name", models.CharField(max_length=150, verbose_name="Имя")),
                ("middle_name", models.CharField(blank=True, max_length=150, verbose_name="Отчество")),
                ("iin", models.CharField(blank=True, db_index=True, max_length=12, null=True, unique=True, verbose_name="ИИН")),
                ("birth_date", models.DateField(verbose_name="Дата рождения")),
                ("sex", models.CharField(choices=[("male", "Мужской"), ("female", "Женский")], max_length=16, verbose_name="Пол")),
                ("phone", models.CharField(blank=True, db_index=True, max_length=32, verbose_name="Телефон")),
                ("address", models.CharField(max_length=255, verbose_name="Адрес")),
                ("settlement_name", models.CharField(max_length=255, verbose_name="Населенный пункт")),
                ("social_category", models.CharField(choices=[("general", "Общая"), ("child", "Ребенок"), ("pregnant", "Беременная"), ("elderly", "Пожилой"), ("disabled", "Лицо с инвалидностью")], default="general", max_length=32, verbose_name="Социальная категория")),
                ("risk_level", models.CharField(choices=[("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий")], default="low", max_length=16, verbose_name="Группа риска")),
                ("attachment_date", models.DateField(verbose_name="Дата прикрепления")),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="patients", to="facilities.facility", verbose_name="Учреждение")),
            ],
            options={"ordering": ["last_name", "first_name"], "verbose_name": "Пациент", "verbose_name_plural": "Пациенты"},
        ),
        migrations.AddIndex(model_name="patient", index=models.Index(fields=["last_name"], name="patients_pa_last_na_0e36b0_idx")),
        migrations.AddIndex(model_name="patient", index=models.Index(fields=["phone"], name="patients_pa_phone_404db2_idx")),
        migrations.CreateModel(
            name="PatientCondition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("condition_name", models.CharField(max_length=255, verbose_name="Состояние")),
                ("icd_code", models.CharField(blank=True, max_length=16, verbose_name="Код МКБ")),
                ("is_chronic", models.BooleanField(default=False, verbose_name="Хроническое")),
                ("diagnosed_at", models.DateField(blank=True, null=True, verbose_name="Дата диагностики")),
                ("notes", models.TextField(blank=True, verbose_name="Примечания")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="conditions", to="patients.patient", verbose_name="Пациент")),
            ],
            options={"ordering": ["condition_name"], "verbose_name": "Состояние пациента", "verbose_name_plural": "Состояния пациентов"},
        ),
    ]
