from api.models import PatientDoctorMapping


class MappingRepository:
    @staticmethod
    def exists(patient, doctor):
        return PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists()

    @staticmethod
    def create(patient, doctor):
        return PatientDoctorMapping.objects.create(patient=patient, doctor=doctor)

    @staticmethod
    def get_all_for_user(user):
        return PatientDoctorMapping.objects.filter(patient__created_by=user)

    @staticmethod
    def get_for_patient(patient):
        return PatientDoctorMapping.objects.filter(patient=patient)

    @staticmethod
    def get_by_id_for_user(mapping_id, user):
        return PatientDoctorMapping.objects.filter(id=mapping_id, patient__created_by=user).first()

    @staticmethod
    def delete(mapping):
        mapping.delete()
