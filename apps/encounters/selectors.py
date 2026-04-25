from django.db.models import QuerySet

from apps.encounters.models import Encounter


def encounter_queryset_for_user(user) -> QuerySet[Encounter]:
    qs = Encounter.objects.select_related("patient", "facility", "clinician", "clinician__user")
    if user.is_superuser:
        return qs
    if hasattr(user, "employee_profile") and user.employee_profile.facility_id:
        qs = qs.filter(facility_id=user.employee_profile.facility_id)
    return qs


def filter_encounters(qs: QuerySet[Encounter], data: dict) -> QuerySet[Encounter]:
    if data.get("date_from"):
        qs = qs.filter(encounter_date__gte=data["date_from"])
    if data.get("date_to"):
        qs = qs.filter(encounter_date__lte=data["date_to"])
    if data.get("facility"):
        qs = qs.filter(facility=data["facility"])
    if data.get("clinician"):
        qs = qs.filter(clinician=data["clinician"])
    if data.get("encounter_type"):
        qs = qs.filter(encounter_type=data["encounter_type"])
    if data.get("patient"):
        qs = qs.filter(patient=data["patient"])
    return qs
