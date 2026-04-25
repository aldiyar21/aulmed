from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=64, verbose_name="Действие")),
                ("entity_type", models.CharField(max_length=64, verbose_name="Сущность")),
                ("entity_id", models.CharField(max_length=64, verbose_name="ID сущности")),
                ("description", models.TextField(verbose_name="Описание")),
                ("changes_json", models.JSONField(blank=True, null=True, verbose_name="Изменения")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="audit_logs", to=settings.AUTH_USER_MODEL, verbose_name="Пользователь")),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "Журнал аудита", "verbose_name_plural": "Журнал аудита"},
        ),
    ]
