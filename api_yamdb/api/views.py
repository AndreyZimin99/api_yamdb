from api.filters import TitleFilters
from django.contrib.auth.tokens import default_token_generator
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from titles.models import Category, Genre, Title
from users.models import User

from .mixins import EmailConfirmationMixin
from .pagination import UserPagination
from .permissions import IsAdmin, IsAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSeriallizer,
                          SignupSerializer, TitleGetSerializer,
                          TitlePostPatchSerializer, TokenSerializer,
                          UserSerializer)


class SignupView(EmailConfirmationMixin, views.APIView):
    """Класс для регистрации пользователя."""

    def post(self, request):
        """Обрабатывает регистрацию."""
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        existing_user = User.objects.filter(email=email).first()

        if existing_user and existing_user.username != username:
            return Response(
                {'email': 'Пользователь с такой почтой уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created and user.email != email:
            return Response(
                {'username': 'Пользователь с таким ником уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.send_confirmation_code(user)

        response_data = (
            serializer.data if created else
            {'message': 'Код подтверждения отправлен повторно'}
        )

        return Response(response_data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """Класс для получения токена."""

    def post(self, request):
        """Обрабатывает получение токена."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if default_token_generator.check_token(user, confirmation_code):
            refresh = RefreshToken.for_user(user)
            return Response(
                {'token': str(refresh.access_token)},
                status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(EmailConfirmationMixin, viewsets.ModelViewSet):
    """Класс для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    pagination_class = UserPagination
    filter_backends = [SearchFilter]
    search_fields = ['username']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get', 'patch', 'delete'], url_path='me')
    def me(self, request):
        """Получение или изменение данных текущего пользователя."""
        if request.method == 'GET':
            user_data = self.get_serializer(request.user).data
            return Response(user_data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_create(self, serializer):
        user = serializer.save()
        user_not_authenticated = not self.request.user.is_authenticated
        user_not_admin = not self.request.user.is_admin()

        if user_not_authenticated or user_not_admin:
            self.send_confirmation_code(user)


class CategoryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    """Получение списка всех категорий"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Получение списка всех жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSeriallizer
    permissions_class = [IsAdminOrReadOnly]
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Получение списка всех произведений"""
    queryset = Title.objects.all()
    permissions_class = [IsAdminOrReadOnly]
    filterset_class = TitleFilters

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlePostPatchSerializer
        return TitleGetSerializer
