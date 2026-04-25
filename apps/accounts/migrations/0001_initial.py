from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("facilities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("position", models.CharField(max_length=255, verbose_name="Должность")),
                ("role_code", models.CharField(choices=[("admin", "Администратор"), ("registrar", "Регистратор"), ("clinician", "Медработник"), ("manager", "Руководитель")], max_length=32, verbose_name="Роль")),
                ("phone", models.CharField(blank=True, max_length=32, verbose_name="Телефон")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("facility", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="employees", to="facilities.facility", verbose_name="Учреждение")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="employee_profile", to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={"verbose_name": "Профиль сотрудника", "verbose_name_plural": "Профили сотрудников"},
        ),
    ]
