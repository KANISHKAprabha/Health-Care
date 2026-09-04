from api.models import Patient


class PatientRepository:
    @staticmethod
    def get_all_for_user(user):
        return Patient.objects.filter(created_by=user)

    @staticmethod
    def get_by_id(patient_id):
        return Patient.objects.filter(id=patient_id).first()

    @staticmethod
    def get_by_id_for_user(patient_id, user):
        return Patient.objects.filter(id=patient_id, created_by=user).first()

    @staticmethod
    def create(data, owner):
        return Patient.objects.create(created_by=owner, **data)

    @staticmethod
    def update(patient, data):
        for field, value in data.items():
            setattr(patient, field, value)
        patient.save()
        return patient

    @staticmethod
    def delete(patient):
        patient.delete()
