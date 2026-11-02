from rest_framework import permissions


class IsProjectOwner(permissions.BasePermission):
    """Only the project's owner can modify it or its tasks."""

    def has_object_permission(self, request, view, obj):
        project = obj if hasattr(obj, "owner") else obj.project
        if request.method in permissions.SAFE_METHODS:
            return True
        return project.owner_id == request.user.id