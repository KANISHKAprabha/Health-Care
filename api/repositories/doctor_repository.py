from api.models import Doctor


class DoctorRepository:
    @staticmethod
    def get_all():
        return Doctor.objects.all()

    @staticmethod
    def get_by_id(doctor_id):
        return Doctor.objects.filter(id=doctor_id).first()

    @staticmethod
    def create(data):
        return Doctor.objects.create(**data)

    @staticmethod
    def update(doctor, data):
        for field, value in data.items():
            setattr(doctor, field, value)
        doctor.save()
        return doctor

    @staticmethod
    def delete(doctor):
        doctor.delete()
