from rest_framework import serializers
from .models import University, Student, Book, Author


class UniversitySerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    # library = serializers.StringRelatedField(many=True)

    class Meta:
        fields = '__all__'
        model = University

    def get_rating(self, obj):
        return obj.library.count() * obj.student_set.count()


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['first_name']
        model = Student


class AuthorSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        fields = ['name', 'students']
        model = Author


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        fields = ['author', 'id']
        model = Book

