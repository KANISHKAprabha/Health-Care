from django.urls import path

from api.views import (
    DoctorDetailView,
    DoctorListCreateView,
    MappingDetailView,
    MappingListCreateView,
    PatientDetailView,
    PatientListCreateView,
)

urlpatterns = [
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<int:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("doctors/<int:doctor_id>/", DoctorDetailView.as_view(), name="doctor-detail"),
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("mappings/<int:id>/", MappingDetailView.as_view(), name="mapping-detail"),
]
