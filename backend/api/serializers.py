from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes import constants
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.models import Subscriptions


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
            and user.subscribers.filter(id=request.user.id)
        )


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeGetSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient'
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient')
    amount = serializers.IntegerField(
        min_value=constants.MIN_VALUE,
        max_value=constants.MAX_VALUE,
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientInRecipeGetSerializer(
        source='ingredientinrecipe_set', many=True
    )

    class Meta:
        model = Recipe
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
    ingredients = IngredientInRecipePostSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_VALUE,
        max_value=constants.MAX_VALUE,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

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

        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=instance,
                ingredient=data_ingredient['id'],
                amount=data_ingredient['amount']
            ) for data_ingredient in ingredients
        ])
        instance.tags.add(*tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.add_tags_and_ingredients(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.add_tags_and_ingredients(
            instance,
            validated_data['tags'],
            validated_data['ingredients']
        )

        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Minified version of RecipeSerializer.

    Fields: 'id', 'name', 'image', and 'cooking_time'.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserWithRecipesSerializer(FoodgramUserSerializer):
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
    subscriber = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Subscriptions
        field = ('subscriber', 'subscribtion')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('subscriber', 'subscribtion'),
                message='Вы уже подписаны!'
            ),
        ]

    def to_representation(self, instance):
        return UserWithRecipesSerializer(
            instance.subscribtion, context=self.context
        ).data

    def validate_subscription(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )

        return value
