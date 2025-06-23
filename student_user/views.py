from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# from .models import Student
# from .serializers import StudentSerializer
from django.core.mail import send_mail
import random

from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser


from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


from django.core.cache import cache

from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib




            

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


@api_view(['POST'])
def student_register_request_otp(request):
    #  create a basic pythom fumction for add data to database and send otp to email before add data verify email existence I donott want to use serializer and model for this function
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    otp = generate_otp()
    data = {
        "email": email,
        "otp": otp,
        "first_name": request.data.get("first_name"),
        "middle_name": request.data.get("middle_name"),
        "last_name": request.data.get("last_name"),
        "date_of_birth": request.data.get("date_of_birth"),
        "contact_number_1": request.data.get("contact_number_1"),
        "contact_number_2": request.data.get("contact_number_2"),
        "student_class": request.data.get("student_class"),
        "school_or_college_name": request.data.get("school_or_college_name"),
        "board_or_university_name": request.data.get("board_or_university_name"),
        "address": request.data.get("address"),
        "city": request.data.get("city"),
        "district": request.data.get("district"),
        "state": request.data.get("state"),
        "pin": request.data.get("pin"),
        "student_photo": request.data.get("student_photo")
    }

    # sql check if email already exists
    # sql = f"""INSERT INTO eduapp.msa_registerd_student (first_name, middle_name, last_name, date_of_birth, contact_number_1, contact_number_2, student_class, school_or_college_name, board_or_university_name, address, city, district, state, pin, notes, email)
    #           VALUES ('{data['first_name']}', '{data['middle_name']}', '{data['last_name']}', '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}', '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}', '{data['address']}', '{data['city']}', '{data['district']}', '{data['state']}', '{data['pin']}',  '{email}')"""
    
    sql = f"""IF NOT EXISTS (
    SELECT 1 FROM eduapp.msa_registerd_student WHERE email = '{email}'
) THEN
    INSERT INTO eduapp.msa_registerd_student (
        first_name, middle_name, last_name, date_of_birth,
        contact_number_1, contact_number_2, student_class,
        school_or_college_name, board_or_university_name,
        address, city, district, state, pin, notes, email, student_photo_path
    ) VALUES (
        '{data['first_name']}', '{data['middle_name']}', '{data['last_name']}',
        '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}',
        '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}',
        '{data['address']}', '{data['city']}', '{data['district']}',
        '{data['state']}', '{data['pin']}', '{data.get('notes', '')}', '{email}', '{data['student_photo']}'
    );
ELSE
    -- Optional: you can raise a signal or do something else
    SELECT 'Email already exists' AS message;
END IF;"""
    
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        # Send OTP email
        otp_data = {
            "otp": otp,
            "data": data
        }
        cache.set(f"student_otp_{email}", otp_data, timeout=OTP_EXPIRY_MINUTES * 60)  # Cache for 10 minutes
        send_otp_email(email, otp)  
        return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
    except Exception as e:  
        print(f"Database error: {e}")
        return Response({"error": "Failed to register student."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def student_confirm_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    cached = cache.get(f"student_otp_{email}")

    if not cached:
        return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

    if cached['otp'] != otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    data = cached['data']
    sql = f"""UPDATE eduapp.msa_registerd_student 
              SET is_verified = 1, student_id = CONCAT('MSA_', DATE_FORMAT(NOW(), '%m%Y'), ID) 
              WHERE email = '{email}'"""
    
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        cache.delete(f"student_otp_{email}")
        return Response({"message": "Registration successful.", "student_id": data['student_id']}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Database error: {e}")
        return Response({"error": "Failed to confirm OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
