from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SignupView, TokenView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

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
