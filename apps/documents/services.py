from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_action
from apps.documents.models import MedicalDocument, PatientFile, Prescription


def _generate_document_number(instance: MedicalDocument) -> str:
    return f"AULMED-DOC-{timezone.now():%Y}-{instance.pk:06d}"


def _generate_prescription_number(instance: Prescription) -> str:
    return f"AULMED-RX-{timezone.now():%Y}-{instance.pk:06d}"


@transaction.atomic
def create_medical_document(*, user, cleaned_data: dict) -> MedicalDocument:
    document = MedicalDocument.objects.create(created_by=user, **cleaned_data)
    if not document.number:
        document.number = _generate_document_number(document)
        if document.status == MedicalDocument.Status.ISSUED and not document.issued_at:
            document.issued_at = timezone.now()
        document.save(update_fields=["number", "issued_at", "updated_at"])
    log_action(
        user=user,
        action="issue_document" if document.status == MedicalDocument.Status.ISSUED else "create",
        entity_type="MedicalDocument",
        entity_id=document.pk,
        description=f"Created medical document {document.number}",
        changes={"status": document.status, "document_type": document.document_type},
    )
    return document


@transaction.atomic
def create_prescription(*, user, cleaned_data: dict, items: list[dict]) -> Prescription:
    prescription = Prescription.objects.create(doctor=user, **cleaned_data)
    if not prescription.number:
        prescription.number = _generate_prescription_number(prescription)
    if prescription.status == Prescription.Status.ISSUED and not prescription.issued_at:
        prescription.issued_at = timezone.now()
    prescription.save(update_fields=["number", "issued_at", "updated_at"])
    prescription_items = []
    for item in items:
        if not item.get("medication_name"):
            continue
        item_payload = {
            key: value
            for key, value in item.items()
            if key not in {"prescription", "id", "DELETE"} and value not in {None, ""}
        }
        prescription_items.append(prescription.items.model(prescription=prescription, **item_payload))
    prescription.items.bulk_create(prescription_items)
    log_action(
        user=user,
        action="issue_prescription" if prescription.status == Prescription.Status.ISSUED else "create",
        entity_type="Prescription",
        entity_id=prescription.pk,
        description=f"Created prescription {prescription.number}",
        changes={"status": prescription.status, "items_count": prescription.items.count()},
    )
    return prescription


def create_patient_file(*, user, cleaned_data: dict) -> PatientFile:
    patient_file = PatientFile.objects.create(uploaded_by=user, **cleaned_data)
    log_action(
        user=user,
        action="upload_file",
        entity_type="PatientFile",
        entity_id=patient_file.pk,
        description=f"Uploaded file {patient_file.title} for patient {patient_file.patient}",
        changes={"result_type": patient_file.result_type, "title": patient_file.title},
    )
    return patient_file
