from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djoser.permissions import CurrentUserOrAdminOrReadOnly


class CurrentUserOrAdminOrReadOnly(
    IsAuthenticatedOrReadOnly, CurrentUserOrAdminOrReadOnly
):
    ...
