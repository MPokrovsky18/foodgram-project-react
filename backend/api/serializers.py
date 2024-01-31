import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, IngredientInRecipe, Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        current_user = self.context.get('request').user

        if current_user and current_user.is_authenticated:
            return user.is_subscriber(current_user)

        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')

    def to_internal_value(self, data):
        if not isinstance(data, int):
            raise serializers.ValidationError("Некорректные данные для тега.")

        return data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True
    )
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_internal_value(self, data):
        if (
            not isinstance(data, dict)
            or 'id' not in data
            or 'amount' not in data
            or not isinstance(data['id'], int)
            or not isinstance(data['amount'], (int, str))
            or (isinstance(data['amount'], str)
                and not data['amount'].isdigit())
        ):
            raise serializers.ValidationError(
                "Некорректные данные для ингредиента."
            )

        if isinstance(data['amount'], str):
            data['amount'] = int(data['amount'])

        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredientinrecipe_set', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

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

    def get_is_favorited(self, recipe):
        current_user = self.context.get('request').user

        if current_user and current_user.is_authenticated:
            return recipe.is_favorited_by_user(current_user)

        return False

    def get_is_in_shopping_cart(self, recipe):
        current_user = self.context.get('request').user

        if current_user and current_user.is_authenticated:
            return recipe.is_added_to_shopping_list_by_user(current_user)

        return False

    def add_tags_and_ingredients(
            self, instance, tags=None, ingredients=None, update=False
    ):
        if ingredients:
            if update:
                instance.ingredientinrecipe_set.all().delete()

            IngredientInRecipe.objects.bulk_create([
                IngredientInRecipe(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(
                        id=data_ingredient['id']
                    ),
                    amount=data_ingredient['amount']
                ) for data_ingredient in ingredients
            ])

        if tags:
            if update:
                instance.tags.clear()

            instance.tags.add(*tags)

        instance.save()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_and_ingredients(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        ingredients = validated_data.get('ingredientinrecipe_set')
        tags = validated_data.get('tags')
        self.add_tags_and_ingredients(instance, tags, ingredients, update=True)

        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class UserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = RecipeMinifiedSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

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

    def get_recipes_count(self, user):
        return user.recipes.count()
