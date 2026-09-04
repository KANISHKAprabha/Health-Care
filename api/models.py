from django.conf import settings
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^\+?\d{7,15}$",
    message="Enter a valid phone number (7-15 digits, optional leading '+').",
)


class Patient(models.Model):
    GENDER_CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(validators=[MaxValueValidator(150)])
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    contact_number = models.CharField(max_length=20, validators=[phone_validator])
    address = models.CharField(max_length=500)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patients"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="mappings")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="mappings")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "doctor")

    def __str__(self):
        return f"{self.patient_id} -> {self.doctor_id}"
