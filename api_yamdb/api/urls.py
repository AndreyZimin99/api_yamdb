from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignupViewSet,
    TitleViewSet,
    TokenViewSet,
    UserViewSet,
)

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('reviews', ReviewViewSet, basename='reviews')
router_v1.register('comments', CommentViewSet, basename='comments')


urlpatterns = [
    path('auth/signup/', SignupViewSet.as_view(), name='signup'),
    path('auth/token/', TokenViewSet.as_view(), name='token'),
    path(
        'users/me/',
        UserViewSet.as_view({'get': 'me', 'patch': 'me', 'delete': 'me'}),
        name='user-me',
    ),
    path('', include(router_v1.urls)),
    path('titles/<int:title_id>/', include(router_v1.urls)),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/',
        include(router_v1.urls),
    ),
]
