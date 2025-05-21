from django.urls import path
from .views import  student_register_request_otp, student_confirm_otp

urlpatterns = [
    # path('register/', student_register),
    path('register/', student_register_request_otp),
    # path('sendotp/', send_otp),
    path('otpverify/', student_confirm_otp),
]
