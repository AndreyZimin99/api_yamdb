from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import permissions, status, views, viewsets, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from .serializers import (SignupSerializer, TokenSerializer, UserSerializer,
                          CategorySerializer, GenreSeriallizer,
                          TitleGetSerializer, TitlePostPatchSerializer)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from titles.models import Category, Genre, Title


class SignupView(views.APIView):
    """Регистрация пользователя."""

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['username'].lower() == 'me':
            return Response(
                {'username': 'Invalid username'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user, created = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email']
        )
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'test@test.ru',
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """Получение токена."""

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=serializer.validated_data['username'])
        if default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']):
            refresh = RefreshToken.for_user(user)
            return Response(
                {'token': str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Invalid code'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Получение информации о пользователях."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Обновление профиля."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if request.user != instance and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action in [
                'list', 'create', 'destroy', 'update', 'partial_update']:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.action == 'retrieve':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_object(self):
        if self.kwargs.get('username') == 'me':
            return self.request.user
        return super().get_object()


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """Получение списка всех категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Получение списка всех жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSeriallizer
    permissions_class = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """Получение списка всех произведений"""
    queryset = Title.objects.all()
    permissions_class = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlePostPatchSerializer
        return TitleGetSerializer
