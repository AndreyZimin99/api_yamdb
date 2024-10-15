from rest_framework import serializers
from users.models import User


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
