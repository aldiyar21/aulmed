# AulMed

AulMed is a Django-based MVP for rural primary healthcare workflows. The project now includes the original internal PHC modules together with a lightweight telemedicine MVP built on Django Templates, HTMX, Bootstrap and public Jitsi Meet rooms.

## Stack

- Python 3.12
- Django 5.2
- PostgreSQL
- Django Templates
- HTMX
- Bootstrap 5.3
- Gunicorn
- Docker Compose
- pytest
- Ruff

## Existing modules

- `core`: dashboards, common layouts, notifications, error pages
- `accounts`: employee profiles, RBAC, demo users, patient login linkage
- `facilities`: medical facilities and settlements
- `patients`: patient registry, chart, patient cabinet pages
- `encounters`: in-person encounters
- `visits`: home visits
- `prevention`: prevention and follow-up workflows
- `referrals`: referrals and routing
- `reports`: operational and telemedicine reporting
- `audit`: audit logging for critical actions
- `appointments`: appointment requests and scheduling
- `telemedicine`: online consultations, consent, teleconsiliums, Jitsi rooms
- `documents`: medical documents, prescriptions, patient files
- `monitoring`: remote vital readings

## Telemedicine MVP

The telemedicine extension keeps the existing AulMed architecture and adds:

- patient login and patient cabinet
- online booking for offline or online appointments
- online consultations with public `meet.jit.si`
- doctor-doctor teleconsiliums
- consent gate for patient telemedicine entry
- medical documents and prescriptions
- patient file uploads and examination results
- remote monitoring by manual vital entry
- telemedicine KPI and CSV export
- basic RU/KK language preparation for the new functionality

## Patient cabinet

The patient account is linked to `Patient.patient_user`. The patient can access:

- patient dashboard
- profile page
- "My card"
- "My encounters"
- "My referrals"
- "My consultations"
- "My documents"
- "My prescriptions"
- "My files"
- "My health indicators"
- appointment booking

Object-level access checks ensure the patient only sees their own records.

## Appointments

The `appointments` app provides:

- patient appointment request creation
- staff queue and appointment detail pages
- doctor appointment list
- support for `offline` and `online` appointment types
- status flow for requested, approved, scheduled, completed, cancelled and no-show states
- automatic creation of an `OnlineConsultation` when an online appointment is scheduled or approved

## Online consultations with Jitsi Meet

The `telemedicine` app uses the public Jitsi Meet deployment:

- `JITSI_DOMAIN` defaults to `meet.jit.si`
- `JITSI_ROOM_PREFIX` defaults to `aulmed`
- room names are generated from UUID-based slugs and do not contain patient PII
- consultation room pages include an embedded meeting and a fallback button to open the room in a new tab
- patients must accept telemedicine consent before entering a consultation room
- doctors can start and complete consultations with manual conclusion fields

For this MVP, no self-hosted Jitsi server is required.

## Medical documents and prescriptions

The `documents` app adds:

- medical certificates, extracts and recommendations
- prescriptions with line items
- printable HTML views for documents and prescriptions
- sequential numbers such as `AULMED-DOC-YYYY-000001` and `AULMED-RX-YYYY-000001`
- patient-facing and staff-facing lists/details

## Remote monitoring

The `monitoring` app adds manual vital reading entry:

- blood pressure
- pulse
- temperature
- SpO2
- glucose
- weight
- comment and timestamp

Patients can enter their own readings. Doctors can review patient readings and add values manually when needed.

## Telemedicine reports

`/reports/telemedicine/` provides filters and KPI cards for:

- total online consultations
- scheduled, completed and cancelled consultations
- average wait time from request to scheduled time
- consultations by facility and settlement
- doctor workload
- issued medical documents
- issued prescriptions
- active monitoring patients
- appointments by status and type
- teleconsilium totals

The page also supports CSV export.

## Demo users

After demo data seeding, the following accounts are available:

- `admin / demo12345`
- `doctor / demo12345`
- `registrator / demo12345`
- `manager / demo12345`
- `patient / demo12345`

The demo patient user is linked to one seeded patient record.

## Env variables

Safe defaults are provided, but you can override them in `.env`:

```env
JITSI_DOMAIN=meet.jit.si
JITSI_ROOM_PREFIX=aulmed
MAX_UPLOAD_SIZE_MB=10
```

Other important variables remain the same as before, including database and Django secret settings.

## Local run without Docker

1. Create a Python 3.12 virtual environment.
2. Install dependencies: `pip install -e .[dev]`
3. Copy `.env.example` to `.env`
4. Start PostgreSQL or set `DATABASE_URL`
5. Apply migrations: `python manage.py migrate`
6. Create demo users: `python manage.py create_demo_users`
7. Load demo data: `python manage.py seed_demo_data`
8. Run the server: `python manage.py runserver`

## Docker Compose

1. Copy `.env.example` to `.env`
2. Start the stack: `docker compose up --build`
3. Run migrations if needed: `docker compose exec web python manage.py migrate`
4. Create demo users: `docker compose exec web python manage.py create_demo_users`
5. Seed demo data: `docker compose exec web python manage.py seed_demo_data`
6. Open `http://localhost:8000`

The compose setup includes a media volume mount:

```text
./media:/app/media
```

This allows uploaded patient files to persist locally in Docker.

## Testing and linting

- `python manage.py makemigrations`
- `python manage.py migrate`
- `pytest`
- `ruff check .`

Tests use `config.settings.test` with SQLite for fast isolated runs.

## Known limitations

- eGov, eHealth, MIS and insurance integrations are not implemented
- AI triage assistant is intentionally not implemented
- Jitsi uses public `meet.jit.si` for local MVP/demo
- app-level RBAC protects access to generated room links
- for production medical use, a self-hosted or authenticated Jitsi deployment should be considered
- PDF generation is not required in this MVP
- mobile app is not implemented, but the web UI is responsive
- the system does not provide automated diagnosis or medical recommendations
