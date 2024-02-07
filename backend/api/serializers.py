from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes import constants, models
from users.models import Subscriptions


class CustomBase64ImageField(Base64ImageField):
    """Custom ImageField for handling base64-encoded images."""

    def to_representation(self, value):
        if value:
            return value.url
        return None


class FoodgramUserSerializer(serializers.ModelSerializer):
    """Custom user serializer."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        request = self.context['request']

        return (
            request
            and request.user.is_authenticated
            and user.subscribers.filter(subscriber=request.user).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient."""

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving ingredient details in a recipe."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipePostSerializer(serializers.ModelSerializer):
    """Serializer for posting ingredient details in a recipe."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=constants.MIN_VALUE,
        max_value=constants.MAX_VALUE,
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Serializer for retrieving recipe data."""

    tags = TagSerializer(many=True, read_only=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientInRecipeGetSerializer(
        source='ingredient_in_recipe', many=True
    )
    image = CustomBase64ImageField()
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True, default=False
    )

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipePostSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipe instances."""

    ingredients = IngredientInRecipePostSerializer(many=True)
    image = CustomBase64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_VALUE,
        max_value=constants.MAX_VALUE,
    )

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError(
                'Изображение - обязательное поле.'
            )

        return value

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context=self.context).data

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')

        if not ingredients or not tags:
            raise serializers.ValidationError(
                'Поля ingredients и tags обязательны.'
            )

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )

        return super().validate(data)

    @staticmethod
    def add_tags_and_ingredients(instance, tags, ingredients):
        instance.tags.clear()
        instance.ingredients.clear()

        models.IngredientInRecipe.objects.bulk_create([
            models.IngredientInRecipe(
                recipe=instance,
                ingredient=data_ingredient['id'],
                amount=data_ingredient['amount']
            ) for data_ingredient in ingredients
        ])
        instance.tags.add(*tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.add_tags_and_ingredients(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        self.add_tags_and_ingredients(
            instance,
            validated_data.pop('tags'),
            validated_data.pop('ingredients')
        )
        instance = super().update(instance, validated_data)

        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Minified version of RecipeSerializer."""

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserWithRecipesSerializer(FoodgramUserSerializer):
    """Serializer for retrieving user data with their recipes."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(FoodgramUserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, user):
        """Retrieve user's recipes with an optional limit."""
        recipes = user.recipes.all()
        recipes_limit = self.context[
            'request'
        ].query_params.get('recipes_limit')

        try:
            if recipes_limit and recipes_limit.isdigit():
                recipes = recipes[:int(recipes_limit)]
        except ValueError:
            pass

        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for managing user subscriptions."""

    class Meta:
        model = Subscriptions
        fields = ('subscriber', 'subscribtion')
        validators = (
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('subscriber', 'subscribtion'),
                message='Вы уже подписаны!'
            ),
        )

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.subscribtion, context=self.context
        ).data

    def validate(self, data):
        if self.context['request'].user == data['subscribtion']:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )

        return data


class BaseFavouritesSerializer(serializers.ModelSerializer):
    """
    Abstract base serializer.

    Use for managing favorites and shopping cart items.
    """

    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        return RecipeMinifiedSerializer(
            instance.recipe, context=self.context
        ).data


class FavoriteSerializer(BaseFavouritesSerializer):
    """Serializer for managing favorite recipes."""

    class Meta(BaseFavouritesSerializer.Meta):
        model = models.Favourites
        validators = (
            UniqueTogetherValidator(
                queryset=models.Favourites.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен!'
            ),
        )


class ShoppingCartSerializer(BaseFavouritesSerializer):
    """Serializer for managing shopping cart items."""

    class Meta(BaseFavouritesSerializer.Meta):
        model = models.ShoppingCart
        validators = (
            UniqueTogetherValidator(
                queryset=models.ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен!'
            ),
        )
