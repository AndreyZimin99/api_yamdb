from rest_framework.pagination import PageNumberPagination

from django.conf import settings


class UserPagination(PageNumberPagination):
    """Пагинация для UserViewSet."""

    page_size = settings.POST_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 100
