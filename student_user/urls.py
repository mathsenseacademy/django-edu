from django.urls import path
# from .views import  student_register_request_otp, student_confirm_otp, student_login, student_register,student_list,verified_student_list,student_detail_by_id, student_register_verify_otp,update_student_detail ,request_student_login_otp
from student_user import views
urlpatterns = [
    # path('register/', student_register),
    path('register/', views.student_register_request_otp),
    # path('sendotp/', send_otp),
    path('otpverify/', views.student_register_verify_otp),
    # path('otpverify/', student_confirm_otp),
    path('login/', views.student_login),
    # path('register/', student_register),
    path('student_list/', views.student_list),
    path('verified_student_list/', views.verified_student_list),
    path('student_detail_by_id/', views.student_detail_by_id),
    path('update_student_detail/', views.update_student_detail),
    path('request_student_login_otp/', views.request_student_login_otp),
    path('verify_student_login_otp/', views.verify_student_login_otp),
]
