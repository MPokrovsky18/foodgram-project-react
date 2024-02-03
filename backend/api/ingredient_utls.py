def get_ingredients_amount(current_user):
    """
    Retrieves a dictionary with the quantity of ingredients.

    Args:
        current_user: FoodgramUser object.

    Returns:
        dict: A dictionary where keys are the names of ingredients
        and values are their total quantity in the shopping list.
    """
    ingredients_amount = dict()

    for recipe in current_user.shopping_list.all():
        ingredients_in_recipe = recipe.ingredientinrecipe_set.all()

        for ingredient in ingredients_in_recipe:
            name, amount = str(ingredient.ingredient), ingredient.amount

            if name not in ingredients_amount:
                ingredients_amount[name] = 0

            ingredients_amount[name] += amount

    return ingredients_amount
