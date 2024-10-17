from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import (SignupView, TokenView, UserViewSet, CategoryViewSet,
                    GenreViewSet, TitleViewSet, CommentViewSet, ReviewViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')

router2_v1 = DefaultRouter()
router3_v1 = DefaultRouter()


router2_v1.register('reviews', ReviewViewSet, basename='reviews')
router3_v1.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path(
        'users/me/',
        UserViewSet.as_view({'get': 'me', 'patch': 'me'}),
        name='user-me'
    ),
    path('', include(router.urls)),
    path('titles/<int:title_id>/', include(router2_v1.urls)),
    path('titles/<int:title_id>/reviews/<int:review_id>/',
         include(router3_v1.urls)),
]
