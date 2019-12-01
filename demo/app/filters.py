from django_filters.rest_framework import filters, filterset

from .models import University, Book, Author


class BookFilter(filterset.FilterSet):
    author = filters.CharFilter(field_name='author__name')
    name = filters.CharFilter(field_name='name', lookup_expr='contains')
    min_pages = filters.NumberFilter(field_name='pages', lookup_expr='gt')
    university = filters.ModelChoiceFilter(queryset=University.objects.all())

    class Meta:
        fields = ['author', 'name', 'min_pages', 'university']
        model = Book



