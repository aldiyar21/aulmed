from django.urls import path

from . import views

urlpatterns = [
    path("my/", views.patient_document_list, name="patient-document-list"),
    path("my/<int:pk>/", views.patient_document_detail, name="patient-document-detail"),
    path("my/prescriptions/", views.patient_prescription_list, name="patient-prescription-list"),
    path("my/prescriptions/<int:pk>/", views.patient_prescription_detail, name="patient-prescription-detail"),
    path("my/files/", views.patient_file_list, name="patient-file-list"),
    path("my/files/upload/", views.patient_file_upload, name="patient-file-upload"),
    path("files/<int:pk>/", views.patient_file_detail, name="patient-file-detail"),
    path("files/<int:pk>/download/", views.patient_file_download, name="patient-file-download"),
    path("staff/", views.staff_document_list, name="staff-document-list"),
    path("staff/create/", views.staff_document_create, name="staff-document-create"),
    path("staff/<int:pk>/", views.staff_document_detail, name="staff-document-detail"),
    path("staff/prescriptions/", views.staff_prescription_list, name="staff-prescription-list"),
    path("staff/prescriptions/create/", views.staff_prescription_create, name="staff-prescription-create"),
    path("staff/prescriptions/<int:pk>/", views.staff_prescription_detail, name="staff-prescription-detail"),
    path("staff/files/upload/", views.staff_file_upload, name="staff-file-upload"),
    path("print/document/<int:pk>/", views.printable_document, name="printable-document"),
    path("print/prescription/<int:pk>/", views.printable_prescription, name="printable-prescription"),
]
