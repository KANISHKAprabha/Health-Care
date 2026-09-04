class DomainError(Exception):
    status_code = 400
    message = "An error occurred."


class PatientNotFoundError(DomainError):
    status_code = 404
    message = "Patient not found."


class DoctorNotFoundError(DomainError):
    status_code = 404
    message = "Doctor not found."


class NotOwnerError(DomainError):
    status_code = 403
    message = "You do not have permission to access this record."


class DuplicateMappingError(DomainError):
    status_code = 400
    message = "This doctor is already assigned to this patient."


class MappingNotFoundError(DomainError):
    status_code = 404
    message = "Mapping not found."


class InvalidCredentialsError(DomainError):
    status_code = 401
    message = "Invalid email or password."
