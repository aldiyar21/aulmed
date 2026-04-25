from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.access import require_access, staff_or_patient_resource_access
from apps.accounts.decorators import patient_required, roles_required
from apps.audit.services import log_action
from apps.documents.forms import (
    MedicalDocumentForm,
    PatientFileForm,
    PrescriptionForm,
    PrescriptionItemFormSet,
)
from apps.documents.selectors import (
    medical_document_queryset_for_user,
    patient_file_queryset_for_user,
    prescription_queryset_for_user,
)
from apps.documents.services import (
    create_medical_document,
    create_patient_file,
    create_prescription,
)
from apps.patients.models import Patient


@patient_required
def patient_document_list(request):
    page_obj = Paginator(medical_document_queryset_for_user(request.user), 15).get_page(request.GET.get("page"))
    return render(request, "documents/patient_document_list.html", {"page_obj": page_obj})


@login_required
def patient_document_detail(request, pk: int):
    document = get_object_or_404(medical_document_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, document))
    return render(request, "documents/patient_document_detail.html", {"document": document})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_document_list(request):
    page_obj = Paginator(medical_document_queryset_for_user(request.user), 20).get_page(request.GET.get("page"))
    return render(request, "documents/staff_document_list.html", {"page_obj": page_obj})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_document_create(request):
    form = MedicalDocumentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        document = create_medical_document(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Документ создан.")
        return redirect("staff-document-detail", pk=document.pk)
    return render(request, "documents/staff_document_form.html", {"form": form, "title": "Создание документа"})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_document_detail(request, pk: int):
    document = get_object_or_404(medical_document_queryset_for_user(request.user), pk=pk)
    return render(request, "documents/staff_document_detail.html", {"document": document})


@login_required
def printable_document(request, pk: int):
    document = get_object_or_404(medical_document_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, document))
    return render(request, "documents/printable_document.html", {"document": document})


@patient_required
def patient_prescription_list(request):
    page_obj = Paginator(prescription_queryset_for_user(request.user), 15).get_page(request.GET.get("page"))
    return render(request, "documents/patient_prescription_list.html", {"page_obj": page_obj})


@login_required
def patient_prescription_detail(request, pk: int):
    prescription = get_object_or_404(prescription_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, prescription))
    return render(request, "documents/patient_prescription_detail.html", {"prescription": prescription})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_prescription_list(request):
    page_obj = Paginator(prescription_queryset_for_user(request.user), 20).get_page(request.GET.get("page"))
    return render(request, "documents/staff_prescription_list.html", {"page_obj": page_obj})


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_prescription_create(request):
    form = PrescriptionForm(request.POST or None)
    formset = PrescriptionItemFormSet(request.POST or None, prefix="items")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        items = [item for item in formset.cleaned_data if item and not item.get("DELETE", False)]
        prescription = create_prescription(user=request.user, cleaned_data=form.cleaned_data, items=items)
        messages.success(request, "Рецепт создан.")
        return redirect("staff-prescription-detail", pk=prescription.pk)
    return render(
        request,
        "documents/staff_prescription_form.html",
        {"form": form, "formset": formset, "title": "Создание рецепта"},
    )


@roles_required("Администратор системы", "Медработник", "Руководитель")
def staff_prescription_detail(request, pk: int):
    prescription = get_object_or_404(prescription_queryset_for_user(request.user), pk=pk)
    return render(request, "documents/staff_prescription_detail.html", {"prescription": prescription})


@login_required
def printable_prescription(request, pk: int):
    prescription = get_object_or_404(prescription_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, prescription))
    return render(request, "documents/printable_prescription.html", {"prescription": prescription})


@patient_required
def patient_file_list(request):
    page_obj = Paginator(patient_file_queryset_for_user(request.user), 15).get_page(request.GET.get("page"))
    return render(request, "documents/patient_file_list.html", {"page_obj": page_obj})


@roles_required("Администратор системы", "Регистратор", "Медработник", "Руководитель")
def staff_file_upload(request):
    form = PatientFileForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        patient_file = create_patient_file(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Файл загружен.")
        return redirect("patient-file-detail", pk=patient_file.pk)
    return render(request, "documents/staff_file_form.html", {"form": form, "title": "Загрузка файла"})


@patient_required
def patient_file_upload(request):
    form = PatientFileForm(request.POST or None, request.FILES or None, initial={"patient": request.user.patient_profile})
    form.fields["patient"].queryset = Patient.objects.filter(pk=request.user.patient_profile.pk)
    form.fields["patient"].initial = request.user.patient_profile
    if request.method == "POST" and form.is_valid():
        patient_file = create_patient_file(user=request.user, cleaned_data=form.cleaned_data)
        messages.success(request, "Файл загружен.")
        return redirect("patient-file-detail", pk=patient_file.pk)
    return render(request, "documents/staff_file_form.html", {"form": form, "title": "Загрузка файла"})


@login_required
def patient_file_detail(request, pk: int):
    patient_file = get_object_or_404(patient_file_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, patient_file))
    log_action(
        user=request.user,
        action="view_file",
        entity_type="PatientFile",
        entity_id=patient_file.pk,
        description=f"Viewed patient file {patient_file.pk}",
        changes={"title": patient_file.title},
    )
    return render(request, "documents/patient_file_detail.html", {"patient_file": patient_file})


@login_required
def patient_file_download(request, pk: int):
    patient_file = get_object_or_404(patient_file_queryset_for_user(request.user), pk=pk)
    require_access(staff_or_patient_resource_access(request.user, patient_file))
    log_action(
        user=request.user,
        action="download_file",
        entity_type="PatientFile",
        entity_id=patient_file.pk,
        description=f"Downloaded patient file {patient_file.pk}",
        changes={"title": patient_file.title},
    )
    return FileResponse(patient_file.file.open("rb"), as_attachment=True, filename=patient_file.file.name.rsplit("/", 1)[-1])
