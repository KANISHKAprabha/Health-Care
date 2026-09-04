import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from api.models import Doctor

DOCTORS_URL = "/api/doctors/"


def detail_url(doctor_id):
    return f"/api/doctors/{doctor_id}/"


@pytest.mark.django_db
def test_create_doctor_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "name": "Dr. Smith", "specialization": "Cardiology",
        "contact_number": "+15555555555", "email": "dr.smith@example.com",
    }

    # Act
    response = client.post(DOCTORS_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_doctor_fail_duplicate_email():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )
    payload = {
        "name": "Dr. Other", "specialization": "Neurology",
        "contact_number": "+15555555555", "email": "dr.smith@example.com",
    }

    # Act
    response = client.post(DOCTORS_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_doctors_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.get(DOCTORS_URL)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]) == 1


@pytest.mark.django_db
def test_get_doctor_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.get(detail_url(doctor.id))

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_doctor_fail_not_found():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)

    # Act
    response = client.get(detail_url(999999))

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_update_doctor_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.put(detail_url(doctor.id), {"specialization": "Neurology"})

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_doctor_fail_invalid_phone():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.put(detail_url(doctor.id), {"contact_number": "not-a-phone"})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_doctor_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    doctor = Doctor.objects.create(
        name="Dr. Smith", specialization="Cardiology",
        contact_number="+15555555555", email="dr.smith@example.com",
    )

    # Act
    response = client.delete(detail_url(doctor.id))

    # Assert
    assert response.status_code == status.HTTP_200_OK
