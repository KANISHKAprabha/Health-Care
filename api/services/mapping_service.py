from django.db import IntegrityError

from api.exceptions import (
    DoctorNotFoundError,
    DuplicateMappingError,
    MappingNotFoundError,
    PatientNotFoundError,
)
from api.repositories.doctor_repository import DoctorRepository
from api.repositories.mapping_repository import MappingRepository
from api.repositories.patient_repository import PatientRepository


class MappingService:
    @staticmethod
    def assign_doctor(patient_id, doctor_id, user):
        patient = PatientRepository.get_by_id_for_user(patient_id, user)
        if patient is None:
            raise PatientNotFoundError()

        doctor = DoctorRepository.get_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundError()

        # Service-level check for the normal path; the DB's unique_together
        # constraint is the final authority against the check-then-act race
        # (see ARCHITECTURE.MD §9).
        if MappingRepository.exists(patient, doctor):
            raise DuplicateMappingError()

        try:
            return MappingRepository.create(patient, doctor)
        except IntegrityError:
            raise DuplicateMappingError()

    @staticmethod
    def list_all_mappings(user):
        return MappingRepository.get_all_for_user(user)

    @staticmethod
    def list_doctors_for_patient(patient_id, user):
        patient = PatientRepository.get_by_id_for_user(patient_id, user)
        if patient is None:
            raise PatientNotFoundError()
        return MappingRepository.get_for_patient(patient)

    @staticmethod
    def remove_mapping(mapping_id, user):
        mapping = MappingRepository.get_by_id_for_user(mapping_id, user)
        if mapping is None:
            raise MappingNotFoundError()
        MappingRepository.delete(mapping)
