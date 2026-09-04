# Healthcare Backend API

A Django + Django REST Framework backend for managing Patients, Doctors, and
Patient–Doctor assignments, with JWT authentication and per-user ownership of
patient records. Built per the decisions recorded in `ARCHITECTURE.MD` — this
file is the practical "how to run it" companion; `ARCHITECTURE.MD` is the
detailed rationale.

## Tech Stack

- Python 3.13, Django, Django REST Framework
- `djangorestframework-simplejwt` — JWT auth
- PostgreSQL (`psycopg2-binary`)
- `django-environ` — `.env`-based configuration

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
cp .env.example .env
# then edit .env with your own SECRET_KEY and Postgres credentials

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
| `SECRET_KEY` | Django secret key | (generate a random one — never reuse the example) |
| `DEBUG` | Django debug mode | `True` for local dev |
| `DB_NAME` | Postgres database name | `healthcare` |
| `DB_USER` | Postgres user | `postgres` |
| `DB_PASSWORD` | Postgres password | — |
| `DB_HOST` | Postgres host | `localhost` |
| `DB_PORT` | Postgres port | `5432` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | Access token lifetime | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token lifetime | `7` |

See `.env.example` for a template.

## Response Envelope

Every response is wrapped uniformly:

```json
// success
{"data": { ... }}

// domain error (not found, not owner, duplicate, etc.)
{"error": {"message": "Patient not found.", "status_code": 404}}

// validation error
{"error": {"message": "{'email': ['This field is required.']}", "status_code": 400}}
```

## Authentication Flow

1. **Register** — creates the user and returns a token pair immediately.
2. **Login** — returns a token pair for an existing user.
3. Send `Authorization: Bearer <access_token>` on every request below (all
   endpoints except `register`/`login`/`token/refresh` require it).
4. When the access token expires, `POST /api/token/refresh/` with the
   refresh token to get a new access token.

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

## API Reference

One sample request/response per resource. Full endpoint list, request bodies
and a runnable end-to-end flow are in `Healthcare-API.postman_collection.json`
(import into Postman — see below).

### Patients (owned per-user)

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
non-existent id gets `404`.

### Doctors (shared, not owned)

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

### Mappings

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

`GET /api/mappings/<patient_id>/` returns the doctors assigned to that
patient; `DELETE /api/mappings/<id>/` removes one mapping by its own id.
Assigning the same doctor to the same patient twice returns `400`
(`DuplicateMappingError`).

## Validation Rules

- `age`: 0–150 (model-level, backed by `PositiveIntegerField` + `MaxValueValidator`)
- `gender`: one of `Male`, `Female`, `Other`
- `contact_number` (Patient and Doctor): digits only, optional leading `+`, 7–15 digits
- `Doctor.email`: unique
- `User.email`: unique (registration)

## Testing with Postman

Import `Healthcare-API.postman_collection.json`. It's organized into `Auth`,
`Patients`, `Doctors`, `Mappings` folders. Run **Login** first (or
**Register** then **Login**) — a post-response script auto-captures
`{{access_token}}`/`{{refresh_token}}` into collection variables, which every
other request uses automatically via collection-level Bearer auth.
`Create Patient`/`Create Doctor`/`Assign Doctor to Patient` likewise
auto-capture `{{patient_id}}`/`{{doctor_id}}`/`{{mapping_id}}` for the
requests that need them.

If you use "Run Collection" top-to-bottom, run the `Mappings` folder before
the `Delete Patient`/`Delete Doctor` requests — deleting a patient or doctor
cascades and removes its mappings.

## Architecture Summary

Full rationale in `ARCHITECTURE.MD`; the key decisions:

- **Two apps, not four.** `accounts` (identity) and `api` (Patient/Doctor/
  Mapping — one bounded context) — splitting the domain further would just
  add cross-app imports without reducing coupling.
- **Custom `User` model** (`AbstractBaseUser` + `PermissionsMixin`,
  `email` as `USERNAME_FIELD`) instead of `AbstractUser`, since the spec's
  fields (name/email/password) don't match Django's default user fields.
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
  GET/PUT/DELETE, not just read. `Doctor` has no owner by design (spec:
  "retrieve all doctors" with no per-user scoping).
- **Defense-in-depth on duplicate mappings**: a service-level `exists()`
  check handles the normal path (clean error message); the DB's
  `unique_together` constraint is the final authority against the
  check-then-act race, with its `IntegrityError` caught and re-raised as the
  same domain error. Duplicate-email registration relies on the DB
  constraint alone — an accepted, lower-priority gap for a rare, one-shot
  action (see `ARCHITECTURE.MD` §9 for the full reasoning).
- **No HTML/templates** — the spec's only testing instruction is
  Postman/an API client, so DRF's browsable API is the only "UI."

### Known deviations from `ARCHITECTURE.MD`'s literal text

- §10 describes a single `DATABASE_URL` parsed via `env.db()`; this project
  uses discrete `DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`
  variables instead, assembled directly into `DATABASES`. Functionally
  equivalent.
- §5 describes an `IsOwner` DRF permission class "applied on Patient
  detail/update/delete views." That class still exists in
  `api/permissions.py`, but ownership enforcement was moved into
  `PatientService` (see above) to keep error messages consistent with every
  other domain rule in the codebase; `IsOwner` is currently unused.
