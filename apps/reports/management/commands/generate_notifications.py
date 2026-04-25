from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.core.models import Notification
from apps.prevention.models import PreventionEvent
from apps.visits.models import HomeVisit


class Command(BaseCommand):
    help = "Генерирует внутренние уведомления"

    def handle(self, *args, **options):
        today = timezone.localdate()
        overdue_events = PreventionEvent.objects.filter(status="overdue").select_related(
            "assigned_employee__user", "patient"
        )
        for event in overdue_events:
            if event.assigned_employee_id:
                Notification.objects.get_or_create(
                    user=event.assigned_employee.user,
                    notification_type="overdue_prevention",
                    title="Просрочено профилактическое мероприятие",
                    body=f"{event.patient}: {event.get_event_type_display()}",
                    due_date=event.planned_date,
                )
        today_visits = HomeVisit.objects.filter(planned_date=today, status="planned").select_related(
            "assigned_employee__user"
        )
        for visit in today_visits:
            Notification.objects.get_or_create(
                user=visit.assigned_employee.user,
                notification_type="today_visit",
                title="Выезд на сегодня",
                body=f"{visit.settlement_name}: {visit.purpose}",
                due_date=today,
            )
        self.stdout.write(self.style.SUCCESS("Уведомления сформированы"))
