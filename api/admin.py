from django.contrib import admin

from api.models import Doctor, Patient, PatientDoctorMapping

admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(PatientDoctorMapping)
