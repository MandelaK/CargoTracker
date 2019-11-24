from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    In our case, admins must be superusers, not only staff users.
    """

    def has_permission(self, request, view):
        """
        The user must be authenticated, a staff user and also a superuser
        """
        return bool(
            request.user and request.user.is_staff and request.user.is_superuser
        )
