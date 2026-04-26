from django.contrib import admin

from .models import OnlineConsultation, PatientConsent, Teleconsilium


@admin.register(OnlineConsultation)
class OnlineConsultationAdmin(admin.ModelAdmin):
    list_display = ("patient", "doctor", "status", "scheduled_start", "facility")
    list_filter = ("status", "facility")
    search_fields = ("patient__last_name", "patient__iin", "doctor__username", "jitsi_room_name")


@admin.register(Teleconsilium)
class TeleconsiliumAdmin(admin.ModelAdmin):
    list_display = ("topic", "patient", "primary_doctor", "status", "scheduled_at")
    list_filter = ("status", "facility")
    filter_horizontal = ("invited_doctors",)


@admin.register(PatientConsent)
class PatientConsentAdmin(admin.ModelAdmin):
    list_display = ("patient", "consultation", "consent_type", "accepted_at", "accepted_by")
    list_filter = ("consent_type",)
