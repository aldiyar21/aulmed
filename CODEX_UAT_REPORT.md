# CODEX UAT Report

## 1. Environment

- Branch: `telemedicine-mvp`
- Python: `3.12.13` inside Docker `web`
- Django: `5.2.13`
- Runtime used for verification: Docker
- Current repo state before UAT: working tree was already dirty; production files had pre-existing local changes before this audit

### Commands Run

```powershell
git status
git branch --show-current
docker compose ps
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_demo_users
docker compose exec web python manage.py seed_demo_data
docker compose exec web python manage.py shell -c "..."
docker compose exec web python --version
docker compose exec web python -c "import django; print(django.get_version())"
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web ruff check .
docker compose exec web python -m pytest -q tests/test_codex_business_flows.py
docker compose exec web python -m pytest -q
```

### Runtime Findings

- `docker compose ps`: `db` and `web` were up.
- `python manage.py migrate`: no unapplied migrations, but Django reported model changes without migration files.
- `python manage.py create_demo_users`: completed successfully.
- `python manage.py seed_demo_data`: completed successfully.
- Demo users confirmed in runtime DB:
  - `admin` -> group `Администратор системы`
  - `doctor` -> group `Медработник`
  - `registrator` -> group `Регистратор`
  - `manager` -> group `Руководитель`
  - `patient` -> group `Пациент`
- `patient` is linked to `Patient.patient_user`:
  - linked patient id: `1`
  - linked patient IIN: `900000000000`
- `python manage.py check`: PASS
- `python manage.py makemigrations --check --dry-run`: FAIL
  - pending migrations detected in:
    - `apps/encounters`
    - `apps/documents`
    - `apps/monitoring`
    - `apps/telemedicine`
- `ruff check .`: FAIL
  - current lint errors are import-order issues in existing project files and also in the new UAT file

### Test Command Status

- Focused UAT run, last confirmed:
  - `docker compose exec web python -m pytest -q tests/test_codex_business_flows.py`
  - result: `10 passed, 1 failed`
- Full repository run, last confirmed:
  - `docker compose exec web python -m pytest -q`
  - result: `59 passed, 1 failed`
- After I added two final smoke checks for admin/anonymous and manager current behavior, Docker re-run was blocked by approval/quota limits, so those two latest assertions are included in the test file but were not re-confirmed by a final container run.

## 2. Test Coverage Summary

| Area | Role | Status | Notes |
| --- | --- | --- | --- |
| Login/dashboard smoke | admin/doctor/registrator/manager/patient | PASS | Confirmed for seeded demo users |
| Anonymous access | anonymous | PARTIAL | Test added, but final rerun blocked by tooling quota; decorators/code indicate redirect to login |
| Patient registry | registrator | PASS | list/create/search/detail/edit/export/duplicate IIN checked |
| Patient chart | doctor/patient | PASS | own chart/profile/dashboard render without 500 |
| Encounters | doctor | PASS | create/edit/export checked |
| Referrals | doctor/patient | PASS | create/edit/export checked; cross-patient source encounter blocked |
| Prevention | doctor | PASS | create/overdue/complete/export checked |
| Home visits | registrator | FAIL | multi-patient create works; edit loses per-patient notes |
| Patient portal | patient | PASS | dashboard/profile/chart/appointments/referrals/docs/files/monitoring render |
| Appointments | patient/staff/doctor | PASS | offline+online create, staff scheduling, doctor list checked |
| Telemedicine | patient/doctor | PASS | consultation auto-created, consent gate works, room renders, no patient PII in room name |
| Documents | doctor/patient | PASS | create/list/detail/print checked |
| Prescriptions | doctor/patient | PASS | create/list/detail/print checked |
| Files | doctor/patient | PASS | staff upload, patient upload, download, tamper attempt checked |
| Monitoring | doctor/patient | PASS | doctor and patient vital entry checked |
| Dashboard/reports | manager | PASS | dashboard, reports, CSV checked |
| Admin access | admin | PARTIAL | smoke test added, but final rerun blocked by tooling quota |
| Privacy / object-level access | patient | PASS | patient cannot access another patient’s appointments, consultation, docs, files, monitoring, staff pages |
| Facility isolation | clinician/manager | PASS / CURRENT BEHAVIOR | clinician is facility-scoped; manager has cross-facility appointment visibility |
| Audit logging | registrator/doctor/patient | PASS | patient create, encounter create, referral create, consent actions logged |
| UI smoke via browser | all | NOT TESTED | Playwright/Selenium tooling was not exposed in this environment |

## 3. Role Results

### Admin

- Confirmed from code and added smoke checks:
  - should open major staff sections
  - no explicit admin-only failures found in code
- Status: `PARTIAL`
  - final rerun of the newly added admin smoke test was blocked by Docker approval/quota limits

### Registrator

- Confirmed:
  - patient registry list/create/search/detail/edit/export works
  - duplicate IIN does not create a second patient
  - home visit create works for multiple patients
- Current behavior from code:
  - registrator is allowed to create/edit encounters
  - registrator is allowed to create/edit referrals
- Status: `PASS` with one cross-module bug in home-visit update flow

### Doctor / Clinician

- Confirmed:
  - encounters create/edit/export
  - referrals create/edit/export
  - prevention create/overdue/complete/export
  - documents/prescriptions/files
  - monitoring
  - telemedicine start/complete
- Status: `PASS`

### Manager

- Confirmed:
  - `/dashboard/`, `/reports/`, `/reports/telemedicine/`, telemedicine CSV
  - read access to key staff lists
- Current behavior:
  - manager can open `/documents/staff/create/`
  - manager can open `/documents/staff/prescriptions/create/`
  - manager can access appointments outside own facility
  - manager can edit staff appointments by route/decorator design
- Status: `PASS` for reporting access; creation/edit rights need business decision

### Patient

- Confirmed:
  - own dashboard/profile/chart
  - own appointments list/detail
  - online consultation consent gate and room
  - own documents/prescriptions/files
  - own vitals
  - object-level privacy against another patient’s resources
- Status: `PASS`

### Anonymous

- Code path:
  - protected views use `login_required`, `patient_required`, or `roles_required`
- Status: `PARTIAL`
  - final runtime rerun of the explicit anonymous smoke check was blocked by approval/quota limits

## 4. Business Flow Results

### Route Map Differences From Requested Scenario

- Actual printable document routes:
  - `/documents/print/document/<id>/`
  - `/documents/print/prescription/<id>/`
- Additional actual monitoring route:
  - `/monitoring/`
- Additional telemedicine routes exist for teleconsiliums.
- `accounts/` and `facilities/` include files exist, but current `urlpatterns` are empty.
- No actual staff edit routes exist for:
  - medical documents
  - prescriptions
- Patient appointment form actual fields are:
  - `facility`
  - `appointment_type`
  - `requested_datetime`
  - `reason`
  - there is no separate `comment` field in the actual form

### Patient Registry

- PASS
- Registrator can create patient with portal account.
- `patient_user` is created and linked on save.

### Patient Chart

- PASS
- Doctor detail page renders linked encounters/referrals/visits/prevention blocks.
- Patient self-chart renders own conditions/encounters/appointments.

### Encounters

- PASS
- Doctor create/edit/export works.
- Encounter is present in doctor patient-card context.

### Referrals

- PASS
- Doctor create/edit/export works.
- Patient sees own referral list.
- Cross-patient `source_encounter` tampering is blocked.

### Home Visits

- FAIL
- Multi-patient creation works.
- Both patients remain attached after edit.
- Per-patient notes are lost after edit.

### Prevention / Risk Groups

- PASS
- Overdue conversion works.
- Completed events stop being overdue.

### Appointments

- PASS
- Patient can create offline and online appointment requests.
- Staff can schedule them.
- Doctor sees assigned appointments.

### Telemedicine / Consent / Jitsi Room

- PASS
- Online appointment gets `OnlineConsultation`.
- Patient is redirected to consent before room access.
- Consent record is stored.
- Room renders without 500.
- Jitsi room name did not include:
  - patient last name
  - IIN
  - phone

### Documents

- PASS
- Doctor can create medical document.
- Patient can see own document and printable view.

### Prescriptions

- PASS
- Doctor can create prescription with items.
- Patient can see own prescription and printable view.

### Files

- PASS
- Staff file upload works.
- Patient file upload works.
- Tampered patient POST does not create a file for another patient.

### Monitoring

- PASS
- Doctor manual reading works.
- Patient manual reading works.
- Own/foreign access behavior is correct for patient.

### Dashboard / Reports / CSV

- PASS
- Manager dashboard/reports render.
- Telemedicine CSV export works.

### RBAC

- PASS with current-behavior caveats
- Notable current behavior:
  - manager document/prescription create pages are accessible
  - manager appointment edit route is intended by decorators/selectors
  - registrator encounter/referral create routes are intended by decorators/selectors

### Privacy

- PASS
- Patient A could not access Patient B direct URLs for:
  - patient detail/edit
  - appointment detail
  - consultation detail/room
  - document detail
  - prescription detail
  - file detail/download
  - staff monitoring patient page

### Facility Isolation

- PASS / CURRENT BEHAVIOR
- Clinician in Facility A could not read Facility B patient detail or appointment detail.
- Encounter CSV for clinician A did not leak Facility B encounter.
- Manager cross-facility appointment access is allowed by current code.

## 5. Bugs Found

### BUG-001

- Severity: `High`
- Area: `Home visits`
- Role: `Registrator / Clinician`
- Title: `Editing a home visit wipes per-patient notes`
- Steps to reproduce:
  1. Create one home visit with two patients.
  2. Save `HomeVisitPatient.notes` for both linked patients.
  3. Open `/visits/<visit_id>/edit/`.
  4. Change only route-level fields such as `route_notes` or `status`.
  5. Save the visit.
- Expected result:
  - existing patient links remain
  - existing per-patient notes remain
- Actual result:
  - links are recreated
  - `HomeVisitPatient.notes` becomes empty
- Evidence:
  - failing test: `tests/test_codex_business_flows.py::test_visit_flow_supports_multiple_patients_and_preserves_links_on_edit`
  - URL under test: `/visits/<id>/edit/`
  - failing assertion:
    - expected `TEST-CODEX patient A outcome`
    - actual `''`
- Suggested fix location:
  - `apps/visits/services.py`
  - probable function: `update_home_visit`
  - current implementation deletes `visit.visit_patients.all()` and recreates links

### BUG-002

- Severity: `Medium`
- Area: `Engineering / Deployability`
- Role: `All`
- Title: `Migration drift present in multiple apps`
- Steps to reproduce:
  1. Run `docker compose exec web python manage.py makemigrations --check --dry-run`
- Expected result:
  - no new migrations needed
- Actual result:
  - Django proposes new migrations for:
    - `encounters`
    - `documents`
    - `monitoring`
    - `telemedicine`
- Evidence:
  - command exited non-zero
- Suggested fix location:
  - generate and review migrations for the listed apps before next deployment/demo

## 6. Potential Business Decisions

- Should manager be allowed to edit staff appointments? Current behavior: `yes`.
- Should manager be allowed to create staff medical documents and prescriptions? Current behavior: `yes`.
- Should manager have cross-facility appointment visibility? Current behavior: `yes`.
- Should registrator be allowed to create encounters and referrals? Current behavior from route decorators: `yes`.
- There are no edit routes for staff documents/prescriptions in the actual code. Is create/detail/print enough for MVP, or is edit required before demo?
- Patient appointment UI does not expose a separate `comment` field. Is `reason` sufficient for MVP?
- Browser UI smoke with Playwright/Selenium was not available here. If demo quality depends on client-side regressions, a separate browser-based pass is still advisable.

## 7. Tests Added / Changed

- Added:
  - `tests/test_codex_business_flows.py`

### Test Functions Added

- `test_demo_seeded_users_login_and_dashboard_smoke`
- `test_admin_access_and_anonymous_redirect_smoke`
- `test_registrator_patient_registry_flow_and_export`
- `test_doctor_encounter_referral_prevention_and_exports`
- `test_visit_flow_supports_multiple_patients_and_preserves_links_on_edit`
- `test_patient_dashboard_appointments_telemedicine_and_room_consent_flow`
- `test_documents_prescriptions_and_files_flow`
- `test_monitoring_flow_for_doctor_and_patient`
- `test_manager_reports_and_current_behavior_permissions`
- `test_patient_privacy_and_object_level_access`
- `test_facility_isolation_for_clinician_exports_and_direct_access`
- `test_audit_logs_are_written_for_key_workflows`

### How To Run

```powershell
docker compose exec web python -m pytest -q tests/test_codex_business_flows.py
docker compose exec web python -m pytest -q
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web ruff check .
```

## 8. Final Recommendation

- Overall status: `Not ready for a clean demo without at least one fix`
- Must fix before demo:
  - `BUG-001` home-visit edit data loss
  - migration drift should be resolved before any deployment or handoff
- Acceptable as MVP limitations only if explicitly agreed:
  - manager can edit appointments and create staff documents/prescriptions
  - manager sees cross-facility appointment data
  - no edit routes for documents/prescriptions
  - no automated browser smoke in this pass

## 9. Notes

- This UAT respected the instruction not to auto-fix business logic bugs.
- No production business logic was changed as part of this audit; only a new automated UAT test file and this report were added.
