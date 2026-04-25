from django.contrib import admin

from .models import HomeVisit, HomeVisitPatient


class HomeVisitPatientInline(admin.TabularInline):
    model = HomeVisitPatient
    extra = 0


@admin.register(HomeVisit)
class HomeVisitAdmin(admin.ModelAdmin):
    list_display = ("planned_date", "settlement_name", "assigned_employee", "status", "facility")
    list_filter = ("status", "facility")
    search_fields = ("settlement_name", "purpose")
    inlines = [HomeVisitPatientInline]
