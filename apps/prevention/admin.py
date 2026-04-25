from django.contrib import admin

from .models import PreventionEvent


@admin.register(PreventionEvent)
class PreventionEventAdmin(admin.ModelAdmin):
    list_display = ("patient", "event_type", "planned_date", "status", "assigned_employee")
    list_filter = ("event_type", "status")
    search_fields = ("patient__last_name", "notes")
