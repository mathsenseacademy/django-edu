from django.urls import path
from .views import student_register

urlpatterns = [
    path('register/', student_register),
]
