import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from api.models import Doctor, Patient, PatientDoctorMapping

MAPPINGS_URL = "/api/mappings/"


def patient_doctors_url(patient_id):
    return f"/api/mappings/{patient_id}/"


def mapping_url(mapping_id):
    return f"/api/mappings/{mapping_id}/"


@pytest.mark.django_db
def test_assign_doctor_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    patient = Patient.objects.create(
        name="Jane Roe", age=30, gender="Female",
        contact_number="+1234567890", address="1 First St", created_by=user,
    )
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.post(MAPPINGS_URL, {"patient": patient.id, "doctor": doctor.id})

    # Assert
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_assign_doctor_fail_duplicate():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    patient = Patient.objects.create(
        name="Jane Roe", age=30, gender="Female",
        contact_number="+1234567890", address="1 First St", created_by=user,
    )
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )
    PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    # Act
    response = client.post(MAPPINGS_URL, {"patient": patient.id, "doctor": doctor.id})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_mappings_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    patient = Patient.objects.create(
        name="Jane Roe", age=30, gender="Female",
        contact_number="+1234567890", address="1 First St", created_by=user,
    )
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )
    PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    # Act
    response = client.get(MAPPINGS_URL)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]) == 1


@pytest.mark.django_db
def test_get_doctors_for_patient_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    patient = Patient.objects.create(
        name="Jane Roe", age=30, gender="Female",
        contact_number="+1234567890", address="1 First St", created_by=user,
    )
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )
    PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    # Act
    response = client.get(patient_doctors_url(patient.id))

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]) == 1


@pytest.mark.django_db
def test_get_doctors_for_patient_fail_not_found():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)

    # Act
    response = client.get(patient_doctors_url(999999))

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_mapping_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    patient = Patient.objects.create(
        name="Jane Roe", age=30, gender="Female",
        contact_number="+1234567890", address="1 First St", created_by=user,
    )
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )
    mapping = PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    # Act
    response = client.delete(mapping_url(mapping.id))

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_mapping_fail_not_found():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)

    # Act
    response = client.delete(mapping_url(999999))

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
