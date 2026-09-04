from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from api.exceptions import DomainError


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(
            {"error": {"message": exc.message, "status_code": exc.status_code}},
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = {"error": {"message": str(response.data), "status_code": response.status_code}}
        return response

    if isinstance(exc, Http404):
        return Response({"error": {"message": "Resource not found.", "status_code": 404}}, status=404)

    return None  # unhandled 500s fall through to Django's default
