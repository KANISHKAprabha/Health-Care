from rest_framework.views import APIView

from api.responses import success_response
from api.serializers import (
    DoctorSerializer,
    MappingListSerializer,
    MappingReadSerializer,
    MappingSerializer,
    PatientSerializer,
)
from api.services.doctor_service import DoctorService
from api.services.mapping_service import MappingService
from api.services.patient_service import PatientService


class PatientListCreateView(APIView):
    def get(self, request):
        patients = PatientService.list_patients(request.user)
        return success_response(PatientSerializer(patients, many=True).data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = PatientService.create_patient(serializer.validated_data, request.user)
        return success_response(PatientSerializer(patient).data, status=201)


class PatientDetailView(APIView):
    def get(self, request, patient_id):
        patient = PatientService.get_patient(patient_id, request.user)
        return success_response(PatientSerializer(patient).data)

    def put(self, request, patient_id):
        patient = PatientService.get_patient(patient_id, request.user)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        patient = PatientService.update_patient(patient, serializer.validated_data)
        return success_response(PatientSerializer(patient).data)

    def delete(self, request, patient_id):
        patient = PatientService.get_patient(patient_id, request.user)
        PatientService.delete_patient(patient)
        return success_response({"message": "Patient deleted."})


class DoctorListCreateView(APIView):
    def get(self, request):
        doctors = DoctorService.list_doctors()
        return success_response(DoctorSerializer(doctors, many=True).data)

    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = DoctorService.create_doctor(serializer.validated_data)
        return success_response(DoctorSerializer(doctor).data, status=201)


class DoctorDetailView(APIView):
    def get(self, request, doctor_id):
        doctor = DoctorService.get_doctor(doctor_id)
        return success_response(DoctorSerializer(doctor).data)

    def put(self, request, doctor_id):
        doctor = DoctorService.get_doctor(doctor_id)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        doctor = DoctorService.update_doctor(doctor, serializer.validated_data)
        return success_response(DoctorSerializer(doctor).data)

    def delete(self, request, doctor_id):
        doctor = DoctorService.get_doctor(doctor_id)
        DoctorService.delete_doctor(doctor)
        return success_response({"message": "Doctor deleted."})


class MappingListCreateView(APIView):
    def get(self, request):
        mappings = MappingService.list_all_mappings(request.user)
        return success_response(MappingListSerializer(mappings, many=True).data)

    def post(self, request):
        serializer = MappingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapping = MappingService.assign_doctor(
            serializer.validated_data["patient"],
            serializer.validated_data["doctor"],
            request.user,
        )
        return success_response(MappingListSerializer(mapping).data, status=201)


class MappingDetailView(APIView):
    """GET treats `id` as a patient_id (doctors for that patient);
    DELETE treats `id` as a mapping_id — matching the spec's shared
    /api/mappings/<id>/ shape for these two actions."""

    def get(self, request, id):
        mappings = MappingService.list_doctors_for_patient(id, request.user)
        return success_response(MappingReadSerializer(mappings, many=True).data)

    def delete(self, request, id):
        MappingService.remove_mapping(id, request.user)
        return success_response({"message": "Mapping deleted."})
