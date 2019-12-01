from rest_framework import viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter

from .filters import BookFilter
from .models import University, Student, Book, Author
from .serializers import UniversitySerializer, StudentSerializer, BookSerializer, AuthorSerializer


class StudentList(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = None


class StudentAPI(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer



class BookAPI(generics.ListAPIView):
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookFilter
    serializer_class = BookSerializer


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['name', 'student']


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = UniversitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

