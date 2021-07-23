from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True
        return request.user == obj.user
