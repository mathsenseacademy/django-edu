from django.urls import path
from manage_batch import views
urlpatterns = [
    path('create_batch/', views.create_batch),
    path('all_batches_with_schedule/', views.all_batches_with_schedule),
    path('batch_detail_by_id/', views.batch_detail_by_id),
    path('update_batch/', views.update_batch),
]
