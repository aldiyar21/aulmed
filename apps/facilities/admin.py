from django.contrib import admin

from .models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("name", "facility_type", "district", "settlement_name", "is_active")
    list_filter = ("facility_type", "district", "is_active")
    search_fields = ("name", "settlement_name", "phone")
