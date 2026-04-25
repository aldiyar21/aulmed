from django.contrib import admin

from .models import Patient, PatientCondition


class PatientConditionInline(admin.TabularInline):
    model = PatientCondition
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "iin", "facility", "settlement_name", "risk_level", "is_active")
    list_filter = ("facility", "sex", "risk_level", "social_category", "is_active")
    search_fields = ("last_name", "first_name", "middle_name", "iin", "phone")
    inlines = [PatientConditionInline]


@admin.register(PatientCondition)
class PatientConditionAdmin(admin.ModelAdmin):
    list_display = ("condition_name", "patient", "is_chronic", "diagnosed_at")
    list_filter = ("is_chronic",)
    search_fields = ("condition_name", "icd_code", "patient__last_name")
