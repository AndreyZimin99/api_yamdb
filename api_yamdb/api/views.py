from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from http import HTTPStatus
from rest_framework import permissions, status, views, viewsets, mixins
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import PAGE_SIZE
from users.models import User
from api.filters import TitleFilters
from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthorOrReadOnly, ReadOnly
from titles.models import Category, Genre, Title
from reviews.models import Review
from .serializers import (SignupSerializer, TokenSerializer, UserSerializer,
                          CategorySerializer, GenreSeriallizer,
                          TitleGetSerializer, TitlePostPatchSerializer,
                          CommentSerializer, ReviewSerializer)


class EmailConfirmationMixin:
    """Миксин для отправки кода подтверждения на почту."""
    @staticmethod
    def send_confirmation_code(user):
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            'noreply@yamdb.com',
            [user.email],
            fail_silently=False,
        )


class SignupView(EmailConfirmationMixin, views.APIView):
    """Класс для регистрации пользователя."""

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        if User.objects.filter(email=email).exists():
            return Response(
                {'email': 'Этот email уже зарегистрирован'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, _ = User.objects.get_or_create(username=username, email=email)
        self.send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(views.APIView):
    """Класс для получения токена."""

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
            {'confirmation_code': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(EmailConfirmationMixin, viewsets.ModelViewSet):
    """Класс для работы с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get', 'patch'],
    )
    def me(self, request):
        """Метод для изменения профиля."""
        if request.method == 'GET':
            return Response(self.get_serializer(request.user).data)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = serializer.save()
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
    
    def get(self, request, *args, **kwargs):
        title = self.get_object()
        serializer = self.get_serializer(title)
        average_rating = title.average_rating()
        response_data = serializer.data
        response_data['rating'] = average_rating
        return Response(response_data)


class BaseViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    pagination_class.page_size = PAGE_SIZE
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ["patch", "get", "post", "delete"]

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class ReviewViewSet(BaseViewSet):
    """Класс для отзыва."""
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        review = Review.objects.filter(title=title,
                                       author=self.request.user)
        if review:
            raise ValidationError(
                'Вы уже отправляли отзыв на это произведение.'
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(BaseViewSet):
    """Класс для комментария."""
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title=self.kwargs['title_id'],
            id=self.kwargs['review_id'],
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title=self.kwargs['title_id'],
            id=self.kwargs['review_id'],
        )
        serializer.save(author=self.request.user, review=review)
