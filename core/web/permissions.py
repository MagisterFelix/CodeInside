from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, SAFE_METHODS

from .utility import DotDict


class IsAdminUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(IsAdminUserOrReadOnly,
                         self).has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


class IsAdminUserOrIsAuthenticated(IsAdminUser):

    def has_permission(self, request, view):
        is_admin = super(IsAdminUserOrIsAuthenticated,
                         self).has_permission(request, view)
        return (request.user.is_authenticated and request.method != "DELETE") or is_admin


permissions = DotDict({
    'AllowAny': AllowAny,
    'IsAuthenticated': IsAuthenticated,
    'IsAdminUser': IsAdminUser,
    'IsAdminUserOrReadOnly': IsAdminUserOrReadOnly,
    'IsAdminUserOrIsAuthenticated': IsAdminUserOrIsAuthenticated
})
