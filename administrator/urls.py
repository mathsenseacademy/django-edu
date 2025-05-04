from django.urls import path
from .views import admin_register, admin_login, admin_student_list
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', admin_register),
    path('login/', admin_login),
    path('students/', admin_student_list),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
