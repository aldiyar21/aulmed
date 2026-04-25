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
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notification_type", models.CharField(max_length=64, verbose_name="Тип")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("body", models.TextField(verbose_name="Текст")),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Срок")),
                ("is_read", models.BooleanField(default=False, verbose_name="Прочитано")),
                ("read_at", models.DateTimeField(blank=True, null=True, verbose_name="Дата прочтения")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "Уведомление", "verbose_name_plural": "Уведомления"},
        ),
    ]
