from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.question_list, name='question-list'),
    path('questions/<int:pk>/', views.question_detail, name='question-detail'),
    path('exams/', views.exam_list, name='exam-list'),
    path('exams/<int:pk>/', views.exam_detail, name='exam-detail'),
    path('exams/<int:exam_id>/add-questions/', views.add_questions_to_exam, name='add-questions'),
    path('exams/<int:exam_id>/questions/', views.exam_questions, name='exam-questions'),
]
