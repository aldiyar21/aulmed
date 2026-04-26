from django.contrib import admin

from .models import MedicalDocument, PatientFile, Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ("number", "patient", "document_type", "status", "issued_at")
    list_filter = ("document_type", "status")
    search_fields = ("number", "title", "patient__last_name", "patient__iin")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("number", "patient", "doctor", "status", "issued_at")
    list_filter = ("status",)
    search_fields = ("number", "patient__last_name", "patient__iin")
    inlines = [PrescriptionItemInline]


@admin.register(PatientFile)
class PatientFileAdmin(admin.ModelAdmin):
    list_display = ("title", "patient", "result_type", "result_date", "uploaded_by")
    list_filter = ("result_type",)
    search_fields = ("title", "patient__last_name", "patient__iin")
