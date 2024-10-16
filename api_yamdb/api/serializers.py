from rest_framework import serializers
from users.models import User
from titles.models import Category, Genre, Title


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    def validate_role(self, value):
        user = self.context['request'].user
        if not user.is_staff and value != 'user':
            raise serializers.ValidationError('У вас нет разрешения.')
        return value

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )


class SignupSerializer(serializers.Serializer):
    """Сериализатор для создания пользователя."""
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        """Проверка уникальности username и email."""
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                'Такое имя пользователя уже существует.')
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Такой email уже существует')
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSeriallizer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSeriallizer()
    # raiting

    class Meta:
        model = Title
        fields = '__all__'


class TitlePostPatchSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'
