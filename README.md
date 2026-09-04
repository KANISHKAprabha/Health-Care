# Healthcare Backend API

A Django + Django REST Framework backend for managing Patients, Doctors, and
Patient–Doctor assignments, with JWT authentication and per-user ownership of
patient records.

## Tech Stack

- Python, Django 6.1.1, Django REST Framework 3.18.0
- `djangorestframework-simplejwt` 5.5.1 — JWT auth
- PostgreSQL (`psycopg2-binary`)
- `django-environ` — `.env`-based configuration
- `pytest` + `pytest-django` — automated tests

## Project Structure

```
config/          Django project: settings, root urls, custom DRF exception handler
accounts/        Identity app — custom User model, register/login
  models.py          Custom User (AbstractBaseUser + PermissionsMixin, email login)
  serializers.py      Register/Login input validation
  services.py          AuthService — issues JWT pairs
  repositories.py     UserRepository — pure data access
  views.py / urls.py  RegisterView, LoginView
api/             Domain app — Patient, Doctor, PatientDoctorMapping
  models.py               Patient, Doctor, PatientDoctorMapping
  serializers.py           Patient/Doctor/Mapping (de)serialization
  services/                business rules, raise domain exceptions
  repositories/            pure data access (return instance or None, never raise)
  views.py / urls.py       APIView subclasses, one per resource
  exceptions.py            DomainError subclasses (uniform error shape)
  permissions.py           IsOwner (defined, currently unused — see below)
  responses.py             success_response() envelope helper
tests/           pytest test suite (auth, patient, doctor, mapping views)
manage.py, pytest.ini, requirements.txt
```

## Architecture

- **Two apps, not four.** `accounts` (identity) and `api` (Patient/Doctor/
  Mapping — one bounded context) — splitting the domain further would just
  add cross-app imports without reducing coupling.
- **Custom `User` model** (`AbstractBaseUser` + `PermissionsMixin`, `email`
  as `USERNAME_FIELD`) instead of `AbstractUser`, since the required fields
  (name/email/password) don't match Django's default user fields.
- **Layered architecture**: view → service → repository → model.
  Repositories are pure data access (return a model instance or `None`,
  never raise); services hold business rules and raise domain exceptions;
  views stay thin (deserialize → call service → wrap in `success_response`).
- **Explicit `APIView` subclasses**, not `ModelViewSet` — keeps the
  view→service call explicit instead of hidden behind generated CRUD.
- **Custom domain exceptions + one exception handler** (`DomainError`
  subclasses in `api/exceptions.py`, wired via `EXCEPTION_HANDLER` in
  settings) produce a single uniform response envelope for every error,
  instead of DRF's default per-exception shapes.
- **Ownership**: `Patient.created_by` is the ownership boundary.
  `PatientService.get_patient(patient_id, user)` raises `PatientNotFoundError`
  (404) if the patient doesn't exist and `NotOwnerError` (403) if it exists
  but isn't the requester's — enforced in the service layer on every
  GET/PUT/DELETE, not just read. `Doctor` has no owner by design (any
  authenticated user can read/update/delete any doctor). `api/permissions.py`
  defines an `IsOwner` DRF permission class, but ownership enforcement lives
  in `PatientService` instead so error messages stay consistent with every
  other domain rule; `IsOwner` is currently unused by any view.
- **Defense-in-depth on duplicate mappings**: `MappingService.assign_doctor`
  first checks `MappingRepository.exists()` for a clean error message on the
  normal path, then relies on the DB's `unique_together` constraint as the
  final authority against the check-then-act race, catching `IntegrityError`
  and re-raising it as the same `DuplicateMappingError`. Duplicate-email
  registration relies on the DB's `unique` constraint alone — no pre-insert
  check — since it's a rare, one-shot action.
- **No HTML/templates** — this is an API-only backend; DRF's browsable API
  is the only "UI."

## Prerequisites

- Python 3.10+
- A running PostgreSQL server, with a database already created (this project
  does **not** create the database for you)

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Create a .env file in the project root (see Environment variables below) —
# there is no .env.example checked in, so create it from scratch.

# 4. Apply migrations
python manage.py migrate

# 5. (optional) create an admin user for /admin/
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/`.

### Environment variables (`.env`)

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | (generate a random one) |
| `DEBUG` | Django debug mode | `True` for local dev |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts (optional; defaults to `*` when `DEBUG=True`, empty otherwise) | `localhost,127.0.0.1` |
| `DB_NAME` | Postgres database name | `healthcare` |
| `DB_USER` | Postgres user | `postgres` |
| `DB_PASSWORD` | Postgres password | — |
| `DB_HOST` | Postgres host (optional, default `localhost`) | `localhost` |
| `DB_PORT` | Postgres port (optional, default `5432`) | `5432` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Access token lifetime (optional, default `60`) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token lifetime (optional, default `7`) | `7` |

`SECRET_KEY`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` are required — the app
will fail to start without them.

## Response Envelope

Every response is wrapped uniformly:

```json
// success
{"data": { ... }}

// domain error (not found, not owner, duplicate, invalid credentials, etc.)
{"error": {"message": "Patient not found.", "status_code": 404}}

// validation error
{"error": {"message": "{'email': ['This field is required.']}", "status_code": 400}}
```

## Authentication Flow

1. **Register** — creates the user and returns a token pair immediately.
2. **Login** — returns a token pair for an existing user.
3. Send `Authorization: Bearer <access_token>` on every request below (all
   endpoints except `register`/`login`/`token/refresh` require it — enforced
   by the project-wide default `IsAuthenticated` permission).
4. When the access token expires, `POST /api/token/refresh/` with the
   refresh token to get a new access token (refresh tokens rotate on use).

```http
POST /api/auth/register/
Content-Type: application/json

{"name": "John Doe", "email": "john@example.com", "password": "SecurePass123"}
```
```json
{"data": {"refresh": "<refresh_token>", "access": "<access_token>"}}
```

```http
POST /api/auth/login/
Content-Type: application/json

{"email": "john@example.com", "password": "SecurePass123"}
```
```json
{"data": {"refresh": "<refresh_token>", "access": "<access_token>"}}
```

Invalid credentials return `401` with `{"error": {"message": "Invalid email or password.", "status_code": 401}}`.

## API Reference

All endpoints below require `Authorization: Bearer <access_token>` unless noted.

### Patients (owned per-user)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/patients/` | List patients created by the current user |
| `POST` | `/api/patients/` | Create a patient (owned by the current user) |
| `GET` | `/api/patients/<id>/` | Retrieve one patient |
| `PUT` | `/api/patients/<id>/` | Update one patient |
| `DELETE` | `/api/patients/<id>/` | Delete one patient |

```http
POST /api/patients/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Jane Roe",
  "age": 30,
  "gender": "Female",
  "contact_number": "+1234567890",
  "address": "1 First St"
}
```
```json
{
  "data": {
    "id": 1, "name": "Jane Roe", "age": 30, "gender": "Female",
    "contact_number": "+1234567890", "address": "1 First St",
    "created_by": 1, "created_at": "2026-09-04T06:13:15.151176Z"
  }
}
```

`GET/PUT/DELETE /api/patients/<id>/` only succeed for the patient's own
creator — any other authenticated user gets `403` (`NotOwnerError`); a
non-existent id gets `404` (`PatientNotFoundError`).

### Doctors (shared, not owned)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/doctors/` | List all doctors |
| `POST` | `/api/doctors/` | Create a doctor |
| `GET` | `/api/doctors/<id>/` | Retrieve one doctor |
| `PUT` | `/api/doctors/<id>/` | Update one doctor |
| `DELETE` | `/api/doctors/<id>/` | Delete one doctor |

```http
POST /api/doctors/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Dr. Smith",
  "specialization": "Cardiology",
  "contact_number": "+15555555555",
  "email": "dr.smith@example.com"
}
```
```json
{
  "data": {
    "id": 1, "name": "Dr. Smith", "specialization": "Cardiology",
    "contact_number": "+15555555555", "email": "dr.smith@example.com",
    "created_at": "2026-09-04T06:13:15.715482Z"
  }
}
```

Any authenticated user can read/update/delete any doctor — doctors are a
shared resource, not per-user.

### Mappings (Patient ↔ Doctor assignments)

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/mappings/` | List all mappings for the current user's patients |
| `POST` | `/api/mappings/` | Assign a doctor to a patient |
| `GET` | `/api/mappings/<patient_id>/` | List doctors assigned to that patient |
| `DELETE` | `/api/mappings/<mapping_id>/` | Remove one mapping by its own id |

```http
POST /api/mappings/
Authorization: Bearer <access_token>
Content-Type: application/json

{"patient": 1, "doctor": 1}
```
```json
{
  "data": {
    "id": 1,
    "patient": { "id": 1, "name": "Jane Roe", "...": "..." },
    "doctor": { "id": 1, "name": "Dr. Smith", "...": "..." },
    "assigned_at": "2026-09-04T06:13:16.227695Z"
  }
}
```

The patient in `POST /api/mappings/` must belong to the requesting user
(`404` `PatientNotFoundError` otherwise); the doctor must exist (`404`
`DoctorNotFoundError` otherwise). Assigning the same doctor to the same
patient twice returns `400` (`DuplicateMappingError`). Note the dual meaning
of `<id>` on `/api/mappings/<id>/`: `GET` treats it as a `patient_id`,
`DELETE` treats it as a `mapping_id`.

## Validation Rules

- `age`: 0–150 (model-level, backed by `PositiveIntegerField` + `MaxValueValidator`)
- `gender`: one of `Male`, `Female`, `Other`
- `contact_number` (Patient and Doctor): digits only, optional leading `+`, 7–15 digits
- `Doctor.email`: unique
- `User.email`: unique (registration)
- `password` (registration): minimum 8 characters

## Testing with pytest

Automated tests use `pytest` + `pytest-django` (see `pytest.ini`, which sets
`DJANGO_SETTINGS_MODULE=config.settings` and picks up `test_*.py` files).
Tests live in `tests/`: `test_auth_views.py`, `test_patient_views.py`,
`test_doctor_views.py`, `test_mapping_views.py`. (`accounts/tests.py` and
`api/tests.py` are unused Django-default stubs.)

```bash
# run the full suite
pytest

# run a single file
pytest tests/test_patient_views.py

# run a single test
pytest tests/test_patient_views.py::test_create_patient_success

# verbose output
pytest -v
```

The suite runs against the database configured in `.env` (via
`pytest-django`, which creates and tears down a test database per run) —
make sure your Postgres credentials in `.env` have permission to create
databases.
