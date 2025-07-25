from django.urls import path
from manage_batch import views
urlpatterns = [
    path('create_batch/', views.create_batch),
    path('all_batches_with_schedule/', views.all_batches_with_schedule),
    path('batch_detail_by_id/', views.batch_detail_by_id),
    path('update_batch/', views.update_batch),
    path('add_batch_fee/', views.add_batch_fee),
    path('all_batch_fee/', views.all_batch_fee),
    path('batch_fee_by_id/', views.update_fee_by_id),
    path('add_student_fee_payment/', views.add_student_fee_payment),
    path('student_fee_status_by_batch/', views.student_fee_status_by_batch),
    path('add_student_fee_status/', views.add_student_fee_status),
    path('month_wise_batch_fee_status/', views.month_wise_batch_fee_status),
]
