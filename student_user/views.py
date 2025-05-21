from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentSerializer
from django.core.mail import send_mail
import random
from django.utils import timezone
from django.core.cache import cache
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

OTP_EXPIRY_MINUTES = 10

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(recipient_email, otp):
    # otp = generate_otp()

    sender_email = 'info@mathsenseacademy.in'  # Hostinger email
    password = 'suvadip#Math25'
    smtp_server = 'smtp.hostinger.com'
    smtp_port = 465  # SSL

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It is valid for 10 minutes."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e
    finally:
        if server:
            server.quit()

    return otp

# Student Registration
# @api_view(['POST'])
# def student_register(request):
#     serializer = StudentSerializer(data=request.data)
#     if serializer.is_valid():
#         student = serializer.save()
#         return Response({'id': student.id}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def send_otp(request):
#     email = request.data.get('email')
#     if not email:
#         return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

#     otp = send_otp_email(email)

#     # Optionally store OTP in DB or cache with expiry
#     return Response({'message': 'OTP sent to email', 'otp': otp})  # Don't return OTP in production

@api_view(['POST'])
def student_register_request_otp(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        print(f"email {email}")

        otp = generate_otp()
        print(f"otp {otp}")

        cache.set(f"student_otp_{email}", {
            'otp': otp,
            'data': serializer.validated_data
        }, timeout=OTP_EXPIRY_MINUTES * 60)

        send_otp_email(email, otp)
        return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def student_confirm_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    cached = cache.get(f"student_otp_{email}")

    if not cached:
        return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

    if cached['otp'] != otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    student = Student.objects.create(**cached['data'], is_verified=True)
    cache.delete(f"student_otp_{email}")

    return Response({"message": "Registration successful.", "student_id": student.student_id}, status=status.HTTP_201_CREATED)
