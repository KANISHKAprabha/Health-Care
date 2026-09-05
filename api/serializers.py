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
   
    patient = serializers.IntegerField()
    doctor = serializers.IntegerField()


class MappingListSerializer(serializers.ModelSerializer):
    

    patient = PatientSerializer()
    doctor = DoctorSerializer()

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "assigned_at"]


class MappingReadSerializer(serializers.ModelSerializer):

    doctor = DoctorSerializer()

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "doctor", "assigned_at"]
