from django.urls import path
from manage_course import views
# from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #batch related urls
    path('create_course/', views.create_course, name='create_course'),
    path('edit_course/', views.edit_course, name='edit_course'),
    path('showcourseid/', views.show_course_by_id, name='show_course_by_id'),
    path('showallcourse/', views.show_all_courses, name='show_all_batch'),
    path('showallactivatecourse/', views.show_all_activate_courses, name='show_all_activate_batch'),

    #course related urls
    # path('createcourses/', views.createcourses, name='create_courses'),
    # path('editcourses/', views.editcourses, name='edit_courses'),
]
