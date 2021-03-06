from rest_framework.permissions import BasePermission, SAFE_METHODS


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


class IsSuperUserOrReadOnly(BasePermission):
    """
    Anyone who is not a superuser only has read access
    """

    def has_permission(self, request, view):

        return (request.method in SAFE_METHODS) or (
            request.user and request.user.is_staff and request.user.is_superuser
        )


class IsRegularUser(BasePermission):
    """
    Only regular users can access this.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and not (
            request.user.is_staff or request.user.is_superuser
        )


class IsStaffOrReadOnly(BasePermission):
    """
    Only staff users have  write access.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated and request.user.is_staff
        )


class IsStaffOrIsAuthenticatedReadOnly(BasePermission):
    """
    Staff users have full access. Authenticated users have only read access.
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_staff or request.method in SAFE_METHODS:
            return True
