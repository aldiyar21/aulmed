from django.contrib import admin

from .models import VitalReading


@admin.register(VitalReading)
class VitalReadingAdmin(admin.ModelAdmin):
    list_display = ("patient", "source", "recorded_at", "systolic_bp", "diastolic_bp", "pulse", "spo2")
    list_filter = ("source",)
    search_fields = ("patient__last_name", "patient__iin")
