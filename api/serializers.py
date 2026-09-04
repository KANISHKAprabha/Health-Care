from rest_framework import serializers

from api.models import Doctor, Patient, PatientDoctorMapping


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "age", "gender", "contact_number", "address", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialization", "contact_number", "email", "created_at"]
        read_only_fields = ["id", "created_at"]


class MappingSerializer(serializers.Serializer):
    """Write serializer — accepts patient/doctor as IDs. Existence and
    ownership are validated in the service layer so failures come back as
    the uniform domain-error envelope rather than a raw DRF PK error."""

    patient = serializers.IntegerField()
    doctor = serializers.IntegerField()


class MappingListSerializer(serializers.ModelSerializer):
    """Read serializer for GET /api/mappings/ — full context per row."""

    patient = PatientSerializer()
    doctor = DoctorSerializer()

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "assigned_at"]


class MappingReadSerializer(serializers.ModelSerializer):
    """Read serializer for GET /api/mappings/<patient_id>/ — the point is
    'which doctors', so only the doctor is nested."""

    doctor = DoctorSerializer()

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "doctor", "assigned_at"]
