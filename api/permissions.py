from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "You do not have permission to access this record."

    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id
