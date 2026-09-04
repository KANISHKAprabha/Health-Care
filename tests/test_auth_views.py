import pytest
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"


@pytest.mark.django_db
def test_register_success():
    # Arrange
    client = APIClient()
    payload = {"name": "John Doe", "email": "john@example.com", "password": "SecurePass123"}

    # Act
    response = client.post(REGISTER_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert "access" in response.data["data"]


@pytest.mark.django_db
def test_register_fail_missing_fields():
    # Arrange
    client = APIClient()
    payload = {"email": "john@example.com"}

    # Act
    response = client.post(REGISTER_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_success():
    # Arrange
    client = APIClient()
    User.objects.create_user(email="jane@example.com", name="Jane", password="SecurePass123")
    payload = {"email": "jane@example.com", "password": "SecurePass123"}

    # Act
    response = client.post(LOGIN_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data["data"]


@pytest.mark.django_db
def test_login_fail_wrong_password():
    # Arrange
    client = APIClient()
    User.objects.create_user(email="jane@example.com", name="Jane", password="SecurePass123")
    payload = {"email": "jane@example.com", "password": "WrongPass1"}

    # Act
    response = client.post(LOGIN_URL, payload)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["error"]["message"] == "Invalid email or password."
