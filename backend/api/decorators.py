from functools import wraps

from rest_framework.response import Response
from rest_framework import status

from api.serializers import RecipeActionSerializer


def recipe_action(method):
    @wraps(method)
    def wrapper(self, request, pk=None):
        recipe = self.get_object()

        if request.method == 'POST':
            serializer = RecipeActionSerializer(recipe)
            method(self, request.user, recipe)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            method(self, request.user, recipe, True)

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(status=status.HTTP_400_BAD_REQUEST)
    return wrapper
