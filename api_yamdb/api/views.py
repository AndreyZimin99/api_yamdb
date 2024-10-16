from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, views, viewsets

from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from .permissions import IsAdmin
from .serializers import SignupSerializer, TokenSerializer, UserSerializer
from titles.models import Review
from api.serializers import CommentSerializer, ReviewSerializer


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


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        titles_id = get_object_or_404(Title, id=self.kwargs['title_id'])
        return titles_id.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title_id=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs['title_id'],
            id=self.kwargs['review_id'],
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs['title_id'],
            id=self.kwargs['review_id'],
        )
        serializer.save(author=self.request.user, review=review)