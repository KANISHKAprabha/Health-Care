from api.exceptions import NotOwnerError, PatientNotFoundError
from api.repositories.patient_repository import PatientRepository


class PatientService:
    @staticmethod
    def list_patients(user):
        return PatientRepository.get_all_for_user(user)

    @staticmethod
    def get_patient(patient_id, user):
        patient = PatientRepository.get_by_id(patient_id)
        if patient is None:
            raise PatientNotFoundError()
        if patient.created_by_id != user.id:
            raise NotOwnerError()
        return patient

    @staticmethod
    def create_patient(data, user):
        return PatientRepository.create(data, owner=user)

    @staticmethod
    def update_patient(patient, data):
        return PatientRepository.update(patient, data)

    @staticmethod
    def delete_patient(patient):
        PatientRepository.delete(patient)
