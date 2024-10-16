from rest_framework import serializers
from users.models import User

from titles.models import Comment, Review


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


class ReviewSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True
    # )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title_id',)


class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True
    # )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title_id', 'review')
