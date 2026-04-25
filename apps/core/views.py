from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.services import user_is_manager_or_admin, user_is_patient
from apps.core.models import Notification
from apps.monitoring.selectors import vital_reading_queryset_for_user
from apps.reports.services import build_dashboard_metrics


def dashboard_redirect(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    if user_is_patient(request.user) and hasattr(request.user, "patient_profile"):
        latest_readings = vital_reading_queryset_for_user(request.user)[:3]
        return render(
            request,
            "core/patient_dashboard.html",
            {"patient": request.user.patient_profile, "latest_readings": latest_readings},
        )
    metrics = build_dashboard_metrics(
        user=request.user,
        date_from=request.GET.get("date_from"),
        date_to=request.GET.get("date_to"),
    )
    return render(
        request,
        "core/dashboard.html",
        {
            "metrics": metrics,
            "today": timezone.localdate(),
            "is_manager_view": user_is_manager_or_admin(request.user),
        },
    )


@login_required
def mark_notification_read(request: HttpRequest, pk: int) -> HttpResponse:
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    next_url = request.GET.get("next") or "dashboard"
    return redirect(next_url)


def permission_denied_view(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "errors/403.html", status=403)


def page_not_found_view(request: HttpRequest, exception=None) -> HttpResponse:
    return render(request, "errors/404.html", status=404)


def server_error_view(request: HttpRequest) -> HttpResponse:
    return render(request, "errors/500.html", status=500)
