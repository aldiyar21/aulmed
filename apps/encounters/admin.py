from django.contrib import admin

from .models import Encounter


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("patient", "facility", "clinician", "encounter_type", "encounter_date", "result_type")
    list_filter = ("encounter_type", "result_type", "facility")
    search_fields = ("patient__last_name", "patient__iin", "reason_for_visit", "diagnosis_text")
