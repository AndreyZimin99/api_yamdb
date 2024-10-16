from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (SignupView, TokenView, UserViewSet, CategoryViewSet,
                    GenreViewSet, TitleViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path(
        'users/me/',
        UserViewSet.as_view({'get': 'me', 'patch': 'me'}),
        name='user-me'
    ),
    path('', include(router.urls)),
]
