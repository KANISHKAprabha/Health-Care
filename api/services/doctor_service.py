from api.exceptions import DoctorNotFoundError
from api.repositories.doctor_repository import DoctorRepository


class DoctorService:
    @staticmethod
    def list_doctors():
        return DoctorRepository.get_all()

    @staticmethod
    def get_doctor(doctor_id):
        doctor = DoctorRepository.get_by_id(doctor_id)
        if doctor is None:
            raise DoctorNotFoundError()
        return doctor

    @staticmethod
    def create_doctor(data):
        return DoctorRepository.create(data)

    @staticmethod
    def update_doctor(doctor, data):
        return DoctorRepository.update(doctor, data)

    @staticmethod
    def delete_doctor(doctor):
        DoctorRepository.delete(doctor)
