from django.urls import path
from .views import  student_register_request_otp, student_confirm_otp, student_login, student_register

urlpatterns = [
    # path('register/', student_register),
    path('register/', student_register_request_otp),
    # path('sendotp/', send_otp),
    path('otpverify/', student_confirm_otp),
    path('login/', student_login),
    path('register/', student_register),
]
