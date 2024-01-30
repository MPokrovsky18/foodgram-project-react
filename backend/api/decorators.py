from functools import wraps

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


def add_remove_action(method):
    @action(detail=True, methods=['post', 'delete'])
    @wraps(method)
    def wrapper(self, request, pk=None, id=None):
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

        return Response(status=status.HTTP_400_BAD_REQUEST)
    return wrapper
