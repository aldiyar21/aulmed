from django.contrib import admin

from .models import Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("patient", "destination_org", "destination_specialist", "priority", "status", "referral_date")
    list_filter = ("priority", "status")
    search_fields = ("patient__last_name", "destination_org", "destination_specialist", "reason")
