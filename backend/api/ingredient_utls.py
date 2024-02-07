from django.template.loader import render_to_string


def get_ingredients_to_txt(user, ingredients_data):
    """Generate a text representation of shopping cart ingredients."""
    return render_to_string(
        'api/shopping_cart.txt',
        {
            'ingredients': ingredients_data,
            'username': user.username
        }
    )
