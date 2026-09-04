import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User

PATIENTS_URL = "/api/patients/"


def detail_url(patient_id):
    return f"/api/patients/{patient_id}/"


@pytest.mark.django_db
def test_create_patient_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    }

    # Act
    response = client.post(PATIENTS_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_patient_fail_invalid_data():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    payload = {
        "name": "Bad Phone", "age": 30, "gender": "Female",
        "contact_number": "abc123", "address": "x",
    }

    # Act
    response = client.post(PATIENTS_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_list_patients_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })

    # Act
    response = client.get(PATIENTS_URL)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["data"]) == 1


@pytest.mark.django_db
def test_list_patients_fail_unauthenticated():
    # Arrange
    client = APIClient()

    # Act
    response = client.get(PATIENTS_URL)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_get_patient_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    created = client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]

    # Act
    response = client.get(detail_url(patient_id))

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_patient_fail_not_found():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)

    # Act
    response = client.get(detail_url(999999))

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_patient_fail_not_owner():
    # Arrange
    owner = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    other = User.objects.create_user(email="other@example.com", name="Other", password="SecurePass123")
    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    created = owner_client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]
    other_client = APIClient()
    other_client.force_authenticate(user=other)

    # Act
    response = other_client.get(detail_url(patient_id))

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_patient_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    created = client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]

    # Act
    response = client.put(detail_url(patient_id), {"address": "New Address"})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["address"] == "New Address"


@pytest.mark.django_db
def test_update_patient_fail_not_owner():
    # Arrange
    owner = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    other = User.objects.create_user(email="other@example.com", name="Other", password="SecurePass123")
    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    created = owner_client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]
    other_client = APIClient()
    other_client.force_authenticate(user=other)

    # Act
    response = other_client.put(detail_url(patient_id), {"address": "Hacked"})

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_patient_success():
    # Arrange
    user = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    client = APIClient()
    client.force_authenticate(user=user)
    created = client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]

    # Act
    response = client.delete(detail_url(patient_id))

    # Assert
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_patient_fail_not_owner():
    # Arrange
    owner = User.objects.create_user(email="owner@example.com", name="Owner", password="SecurePass123")
    other = User.objects.create_user(email="other@example.com", name="Other", password="SecurePass123")
    owner_client = APIClient()
    owner_client.force_authenticate(user=owner)
    created = owner_client.post(PATIENTS_URL, {
        "name": "Jane Roe", "age": 30, "gender": "Female",
        "contact_number": "+1234567890", "address": "1 First St",
    })
    patient_id = created.data["data"]["id"]
    other_client = APIClient()
    other_client.force_authenticate(user=other)

    # Act
    response = other_client.delete(detail_url(patient_id))

    # Assert
    assert response.status_code == status.HTTP_403_FORBIDDEN
