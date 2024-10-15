from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение только для администратора."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение только для автора."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.role in [
            'admin', 'moderator']
