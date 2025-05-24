from django.urls import path
from examportal import views
# from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    #question related urls
    path('createquestions/', views.createquestion, name='create_questions'),
    path('editquestions/', views.editquestion, name='edit_questions'),
    path('getquestions/', views.getquestions, name='get activate questions details'),
    path('getallquestions/', views.getallquestions, name='getallquestions'),
    path('getquestionbyid/', views.getquestionbyid, name='getquestionbyid'),
    # Answer related urls
    path('createanswer/', views.create_answer, name='create_answer'),
    
]
