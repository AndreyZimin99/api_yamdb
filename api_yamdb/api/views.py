from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilters
from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User
from .mixins import EmailConfirmationMixin
from .pagination import UserPagination
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleGetSerializer,
    TitlePostPatchSerializer,
    TokenSerializer,
    UserSerializer,
)


class SignupViewSet(EmailConfirmationMixin, views.APIView):
    """Класс для регистрации пользователя."""

    def post(self, request):
        """Обрабатывает регистрацию."""
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        if self._is_email_taken(email, username):
            return Response(
                {'email': 'Пользователь с такой почтой уже существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = self._get_or_create_user(username, email)

        if not created and user.email != email:
            return Response(
                {'username': 'Пользователь с таким ником уже существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.send_confirmation_code(user)
        except Exception:
            return Response(
                {'error': 'Ошибка при отправке кода подтверждения'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return self._prepare_response(created, serializer)

    def _is_email_taken(self, email, username):
        """Проверяет, занят ли email другим пользователем."""
        existing_user = User.objects.filter(email=email).first()
        return existing_user and existing_user.username != username

    def _get_or_create_user(self, username, email):
        """Cоздает нового пользователя или получает существующего"""
        return User.objects.get_or_create(
            username=username, defaults={'email': email}
        )

    def _prepare_response(self, created, serializer):
        """Ответ в зависимости от того, был ли создан новый пользователь."""
        response_data = (
            serializer.data
            if created
            else {'message': 'Код подтверждения отправлен повторно'}
        )
        return Response(response_data, status=status.HTTP_200_OK)


class TokenViewSet(views.APIView):
    """Класс для получения токена."""

    def post(self, request):
        """Обрабатывает получение токена."""
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)

        if default_token_generator.check_token(user, confirmation_code):
            refresh = RefreshToken.for_user(user)
            return Response(
                {'token': str(refresh.access_token)}, status=status.HTTP_200_OK
            )

        return Response(
            {'error': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST,
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
        user_not_admin = not self.request.user.is_admin

        if user_not_authenticated or user_not_admin:
            self.send_confirmation_code(user)


class CategoryViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Получение списка всех категорий"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ['name']
    lookup_field = 'slug'


class GenreViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Получение списка всех жанров"""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ['name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Получение списка всех произведений"""

    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = TitleFilters
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_queryset(self):
        return (
            Title.objects.all()
            .select_related('category')
            .prefetch_related('genre')
            .annotate(rating=Avg('reviews__score'))
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlePostPatchSerializer
        return TitleGetSerializer


class BaseViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для отзывов и комментариев."""

    pagination_class = PageNumberPagination
    pagination_class.page_size = settings.POST_PER_PAGE
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ['patch', 'get', 'post', 'delete']

    def get_permissions(self):
        """Доступ к отдельному объекту при GET-запросе."""
        if self.action == 'retrieve':
            return (IsAdminOrReadOnly(),)
        return super().get_permissions()


def get_review(self):
    return get_object_or_404(
        Review,
        title=self.kwargs['title_id'],
        id=self.kwargs['review_id'],
    )


class ReviewViewSet(BaseViewSet):
    """Класс для отзыва."""

    serializer_class = ReviewSerializer

    def get_queryset(self):
        """Получение списка отзывов."""
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        review = Review.objects.filter(title=title, author=self.request.user)
        if review:
            raise ValidationError(
                'Вы уже отправляли отзыв на это произведение.'
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(BaseViewSet):
    """Класс для комментария."""

    serializer_class = CommentSerializer

    def get_queryset(self):
        """Получение списка комментариев."""
        review = get_review(self)
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_review(self)
        serializer.save(author=self.request.user, review=review)
