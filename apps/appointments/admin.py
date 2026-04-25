from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "appointment_type", "status", "requested_datetime", "scheduled_datetime", "doctor")
    list_filter = ("appointment_type", "status")
    search_fields = ("patient__last_name", "patient__iin", "doctor__username")
