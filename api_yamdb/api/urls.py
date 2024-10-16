from django.urls import include, path
from rest_framework import routers

from api.views import (
    CommentViewSet, ReviewViewSet
)

router2_v1 = routers.DefaultRouter()
router3_v1 = routers.DefaultRouter()


router2_v1.register('reviews', ReviewViewSet, basename='reviews')
router3_v1.register('comments', CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/titles/<int:title_id>/', include(router2_v1.urls)),
    path('v1/titles/<int:title_id>/reviews/<int:review_id>/',
         include(router3_v1.urls)),
]
