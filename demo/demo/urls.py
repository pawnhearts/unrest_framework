from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from app.views import StudentViewSet, UniversityViewSet, BookAPI, StudentList, StudentAPI


router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'universities', UniversityViewSet)

urlpatterns = [
    path('api/', include('app.urls')),
]
urlpatterns += router.urls

