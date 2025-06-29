from django.urls import path
from .views import  student_register_request_otp, student_confirm_otp, student_login, student_register,student_list,verified_student_list,student_detail_by_id, student_register_verify_otp

urlpatterns = [
    # path('register/', student_register),
    path('register/', student_register_request_otp),
    # path('sendotp/', send_otp),
    path('otpverify/', student_register_verify_otp),
    # path('otpverify/', student_confirm_otp),
    path('login/', student_login),
    # path('register/', student_register),
    path('student_list/', student_list),
    path('verified_student_list/', verified_student_list),
    path('student_detail_by_id/', student_detail_by_id),
]
