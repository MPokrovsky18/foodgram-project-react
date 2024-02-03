from functools import wraps

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


def add_remove_action(method):
    """
    Decorator for adding custom POST and DELETE actions to viewset.

    Usage:
    ```python
    @add_remove_action
    def custom_action(self, user, target_object, remove=False):
        # Custom logic for the action
    ```

    Returns:
        - Response: HTTP response object with appropriate status and data.
    """
    @action(detail=True, methods=['post', 'delete'])
    @wraps(method)
    def wrapper(self, request, pk=None, id=None):
        try:
            target_object = self.get_object()

            if request.method == 'POST':
                serializer = self.get_serializer(target_object)
                method(self, request.user, target_object)

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            if request.method == 'DELETE':
                method(self, request.user, target_object, True)

                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )
        except ValidationError as exseption:
            return Response(
                {'error': exseption.message},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
    return wrapper
