from titles.models import Title

from rest_framework import filters

class TitleFilters(filters.Filterset):
    category = filters.CharFilter(
        field_name='category__slug',
        lookup_expr='icontains'
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = filters.NumberFilter(
        field_name='year',
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = '__all__'