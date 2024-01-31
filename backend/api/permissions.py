from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from djoser.permissions import CurrentUserOrAdminOrReadOnly


class CurrentUserOrAdminOrReadOnly(
    IsAuthenticatedOrReadOnly, CurrentUserOrAdminOrReadOnly
):
    pass


class IsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
