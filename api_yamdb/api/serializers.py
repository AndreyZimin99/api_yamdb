from rest_framework import serializers
from users.models import User
from titles.models import Category, Genre, Title


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
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        """Проверка имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return value


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
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'
