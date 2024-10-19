from rest_framework.pagination import PageNumberPagination

from api_yamdb.settings import PAGE_SIZE


class UserPagination(PageNumberPagination):
    """Пагинация для UserViewSet."""
    page_size = PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100
