from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly


class CurrentUserOrAdminOrReadOnly(
    IsAuthenticatedOrReadOnly, CurrentUserOrAdminOrReadOnly
):
    """
    Combined permission class.

    Allowing read access to unauthenticated users
    and write access to the current user or admin.
    """

    pass


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """
    Permission class allowing write access only to the author.

    Read access to all users.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
