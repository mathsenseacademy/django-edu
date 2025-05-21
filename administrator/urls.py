from django.urls import path
from .views import admin_register, admin_login, admin_student_list, create_course_type, list_course_types, create_course, list_courses
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', admin_register),
    path('login/', admin_login),
    path('students/', admin_student_list),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('createCourseType/', create_course_type, name='cuorse_type'),
    path('courseTypeList/', list_course_types, name='cuorse_type'),
    path('createCourse/', create_course, name='token_refresh'),
    path('courseList/', list_courses, name='token_refresh'),
]
