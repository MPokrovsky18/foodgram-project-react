import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, IngredientInRecipe, Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
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
        print(data)
        if (
            not isinstance(data, dict)
            or 'id' not in data
            or 'amount' not in data
            or not isinstance(data['id'], int)
            or (isinstance(data['amount'], str)
                and not data['amount'].isdigit())
            or (not isinstance(data['amount'], str)
                and not isinstance(data['amount'], int))
        ):
            raise serializers.ValidationError(
                "Некорректные данные для ингредиента."
            )

        if isinstance(data['amount'], str):
            data['amount'] = int(data['amount'])

        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
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

    def create(self, validated_data):
        if (
            'ingredients' not in self.initial_data
            or 'tags' not in self.initial_data
        ):
            raise ValidationError(
                'Поля "ingredients" и "tags" являются обязательными.'
            )

        ingredients = validated_data.pop('ingredientinrecipe_set')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for data_ingredient in ingredients:
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=data_ingredient['id']),
                amount=data_ingredient['amount']
            )

        for tag_id in tags:
            recipe.tags.add(Tag.objects.get(id=tag_id))

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

        if ingredients:
            instance.ingredientinrecipe_set.all().delete()

            for data_ingredient in ingredients:
                IngredientInRecipe.objects.create(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(
                        id=data_ingredient['id']
                    ),
                    amount=data_ingredient['amount']
                )

        if tags:
            instance.tags.clear()

            for tag_id in tags:
                instance.tags.add(Tag.objects.get(id=tag_id))

        instance.save()

        return instance


class RecipeActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)
