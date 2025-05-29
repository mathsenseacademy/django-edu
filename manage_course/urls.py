from django.urls import path
from manage_course import views
# from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #batch related urls
    path('createbatches/', views.batches, name='create_batches'),
    path('editbatches/', views.editbatchs, name='edit_batches'),

    #course related urls
    path('createcourses/', views.createcourses, name='create_courses'),
    path('editcourses/', views.editcourses, name='edit_courses'),
]
