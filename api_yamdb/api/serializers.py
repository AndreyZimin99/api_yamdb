import re

from rest_framework import serializers
from titles.models import Category, Genre, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)

    def validate_role(self, value):
        """Проверка роли пользователя."""
        user = self.context['request'].user
        if not user.is_admin() and value != user.role:
            raise serializers.ValidationError('Вы не можете поменять роль')
        return value


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина имени пользователя не должна превышать 150 символов')
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Имя пользователя содержит недопустимые символы')
        return value

    def validate_email(self, value):
        """Проверка email."""
        if len(value) > 254:
            raise serializers.ValidationError(
                'Длина email не должна превышать 254 символа')

        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для получения категории."""
    class Meta:
        model = Category
        fields = '__all__'


class GenreSeriallizer(serializers.ModelSerializer):
    """Сериализатор для получения жанров."""
    class Meta:
        model = Genre
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка произведений."""
    category = CategorySerializer(read_only=True)
    genre = GenreSeriallizer(read_only=True)
    raiting = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostPatchSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и обновления произведений."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'
