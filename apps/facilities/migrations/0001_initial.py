from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Facility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                ("facility_type", models.CharField(choices=[("fap", "ФАП"), ("ambulatoria", "Амбулатория"), ("clinic", "Поликлиника"), ("other", "Другое")], max_length=32, verbose_name="Тип")),
                ("region", models.CharField(max_length=255, verbose_name="Регион")),
                ("district", models.CharField(max_length=255, verbose_name="Район")),
                ("settlement_name", models.CharField(max_length=255, verbose_name="Населенный пункт")),
                ("address", models.CharField(max_length=255, verbose_name="Адрес")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активно")),
            ],
            options={"ordering": ["name"], "verbose_name": "Учреждение", "verbose_name_plural": "Учреждения"},
        ),
    ]
