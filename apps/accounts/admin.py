from django.contrib import admin

from .models import EmployeeProfile


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "facility", "position", "role_code", "is_active")
    list_filter = ("role_code", "facility", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "position")
