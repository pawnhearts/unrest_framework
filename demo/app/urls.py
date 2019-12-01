from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from app.views import StudentViewSet, UniversityViewSet, BookAPI, StudentList, StudentAPI

urlpatterns = [
    url(r'student_list/', StudentList.as_view()),
    url(r'student/{pk}', StudentAPI.as_view()),
    url(r'books/', BookAPI.as_view()),
]
