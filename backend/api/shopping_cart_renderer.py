from django.http import FileResponse
from django.template.loader import render_to_string


def render_shopping_cart_as_txt(user, ingredients_data):
    """
    Render the shopping cart content as a text file.

    Args:
        - user:
            The user for whom the shopping cart is rendered.
        - ingredients_data:
            The data representing the ingredients in the shopping cart.

    Returns:
        - FileResponse: A FileResponse containing the rendered text file.
    """
    return FileResponse(
        render_to_string(
            'api/shopping_cart.txt',
            {
                'ingredients': ingredients_data,
                'username': user.username
            }
        ),
        content_type='text/plain'
    )
