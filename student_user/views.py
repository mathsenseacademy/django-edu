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
from .models import StudentCredential
from .serializers import StudentCredentialSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser


from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


from django.core.cache import cache

from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from django.utils import timezone

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
        print(e)
        print(f"Failed to send email: {e}")
        raise e
    finally:
        if server:
            server.quit()
    print("OTP SEND")
    return otp




@api_view(['POST'])
def student_register_request_otp(request):
    #  create a basic pythom fumction for add data to database and send otp to email before add data verify email existence I donott want to use serializer and model for this function
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    print(f"email {email}")
    otp = generate_otp()
    print(otp)
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
        "pin": request.data.get("pin")
    }

    # sql check if email already exists
    # sql = f"""INSERT INTO eduapp.msa_registerd_student (first_name, middle_name, last_name, date_of_birth, contact_number_1, contact_number_2, student_class, school_or_college_name, board_or_university_name, address, city, district, state, pin, notes, email)
    #           VALUES ('{data['first_name']}', '{data['middle_name']}', '{data['last_name']}', '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}', '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}', '{data['address']}', '{data['city']}', '{data['district']}', '{data['state']}', '{data['pin']}',  '{email}')"""
    
    sql = f"""
    INSERT INTO eduapp.msa_registerd_student (
        first_name, middle_name, last_name, date_of_birth,
        contact_number_1, contact_number_2, student_class,
        school_or_college_name, board_or_university_name,
        address, city, district, state, pin, notes, email, student_type
    ) SELECT 
        '{data['first_name']}', '{data['middle_name']}', '{data['last_name']}',
        '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}',
        '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}',
        '{data['address']}', '{data['city']}', '{data['district']}',
        '{data['state']}', '{data['pin']}', '{data.get('notes', '')}', '{email}', 'discontinue'

      FROM DUAL
    WHERE NOT EXISTS (
    SELECT 1 FROM eduapp.msa_registerd_student WHERE email = '{email}'
    )  
    ;
;"""
#     sql = f"""IF NOT EXISTS (
#     SELECT 1 FROM msa_registerd_student WHERE email = {email}
# ) THEN
#     INSERT INTO eduapp.msa_registerd_student (
#         first_name, middle_name, last_name, date_of_birth,
#         contact_number_1, contact_number_2, student_class,
#         school_or_college_name, board_or_university_name,
#         address, city, district, state, pin, notes, email, student_type
#     ) VALUES (
#         '{data['first_name']}', '{data['middle_name']}', '{data['last_name']}',
#         '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}',
#         '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}',
#         '{data['address']}', '{data['city']}', '{data['district']}',
#         '{data['state']}', '{data['pin']}', '{data.get('notes', '')}', '{email}', 'discontinue'
#     );
# ELSE
#     -- Optional: you can raise a signal or do something else
#     SELECT 'Email already exists' AS message;
# END IF;"""
    print(f"sql: {sql}")
    # sql = """
    #     INSERT INTO eduapp.msa_registerd_student (
    #         first_name, middle_name, last_name, date_of_birth,
    #         contact_number_1, contact_number_2, student_class,
    #         school_or_college_name, board_or_university_name,
    #         address, city, district, state, pin, notes, email, student_type
    #     )
    #     SELECT %s, %s, %s, %s,
    #            %s, %s, %s,
    #            %s, %s,
    #            %s, %s, %s, %s, %s, %s, %s, %s
    #     FROM DUAL
    #     WHERE NOT EXISTS (
    #         SELECT 1 FROM eduapp.msa_registerd_student WHERE email = %s
    #     )
    #     """

    # params = [
    #         data['first_name'], data['middle_name'], data['last_name'], data['date_of_birth'],
    #         data['contact_number_1'], data['contact_number_2'], data['student_class'],
    #         data['school_or_college_name'], data['board_or_university_name'],
    #         data['address'], data['city'], data['district'], data['state'], data['pin'],
    #         data.get('notes', ''), email, 'discontinue',
    #         email  # used in the WHERE NOT EXISTS
    #     ]





    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        # cursor.execute(sql, params)
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


def generate_jwt_for_student(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
def student_confirm_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    # Step 1: Check OTP in cache
    cached = cache.get(f"student_otp_{email}")
    if not cached:
        return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

    if cached['otp'] != otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    data = cached['data']

    try:
        # Step 2: Mark student as verified
        with connection.cursor() as cursor:
            cursor.execute("SELECT ID FROM eduapp.msa_registerd_student WHERE email = %s", [email])
            row = cursor.fetchone()
            if not row:
                return Response({"error": "Student not found in registration table."}, status=status.HTTP_404_NOT_FOUND)
            student_db_id = row[0]

            # Generate student_id string
            formatted_id = f"MSA_{datetime.now().strftime('%m%Y')}{student_db_id}"

            # Update verified and student_id
            cursor.execute("""
                UPDATE eduapp.msa_registerd_student 
                SET is_verified = 1, student_id = %s
                WHERE ID = %s
            """, [formatted_id, student_db_id])
            connection.commit()

        # Step 3: Register student in msa_student_credentials using serializer
        credential_data = {
            "student_id": student_db_id,
            "student_username": email,
            "student_password": f"{data['first_name']}{datetime.strptime(data['date_of_birth'], '%Y-%m-%d').year}",
            "is_active": True,
            "last_login": timezone.now()
        }

        serializer = StudentCredentialSerializer(data=credential_data)
        if serializer.is_valid():
            student = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(f"student_otp_{email}")

        # Step 4: Generate JWT and respond
        tokens = generate_jwt_for_student(student)

        return Response({
            "message": "Student registered and verified successfully.",
            "student_id": student_db_id,
            "username": email,
            **tokens
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to complete OTP confirmation and registration."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def generate_jwt_for_student(user):
#     refresh = RefreshToken.for_user(user)
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }

@api_view(['POST'])
def student_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        student = StudentCredential.objects.get(student_username=email, student_password=password, is_active=True)
        student.last_login = timezone.now()
        student.save(update_fields=['last_login'])

        tokens = generate_jwt_for_student(student)
        return Response({
            "message": "Login successful",
            "student_id": student.student_id,
            "username": student.student_username,
            **tokens
        })
    except StudentCredential.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def student_register(request):
    serializer = StudentCredentialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(is_active=True)
        return Response({"message": "Student registered successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# def student_confirm_otp(request):
#     email = request.data.get("email")
#     otp = request.data.get("otp")

    

#     # Find ID
#     id_sql =f"SELECT ID FROM eduapp.msa_registerd_student WHERE email = '{email}'"
#     print(id_sql)
#     student_id=0
#     try:
#         cursor = connection.cursor()
#         cursor.execute(id_sql)
#         result = cursor.fetchone()
#         student_id = result[0]
#         print(f"student_id: {student_id}")
#         connection.commit()
#         cursor.close()
        
#         return Response({"message": "Registration successful.", "student_id": data['student_id']}, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         print(f"Database error: {e}")
#         return Response({"error": "Failed to confirm OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
#     cached = cache.get(f"student_otp_{email}")
#     if not cached:
#         return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

#     if cached['otp'] != otp:
#         return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

#     data = cached['data']
#     sql = f"""UPDATE msa_registerd_student 
#               SET is_verified = 1, student_id = CONCAT('MSA_', DATE_FORMAT(NOW(), '%m%Y'), ID) 
#               WHERE ID = '{student_id}'"""
   
#     print(f"sql: {sql}")
#     try:
#         cursor = connection.cursor()
#         cursor.execute(sql)
#         connection.commit()
#         cursor.close()
#         cache.delete(f"student_otp_{email}")
#         return Response({"message": "Registration successful.", "student_id": data['student_id']}, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         print(f"Database error: {e}")
#         return Response({"error": "Failed to confirm OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_list(request):
    try:
        cursor = connection.cursor()
        sql = """
            SELECT 
                ID, student_id, first_name, middle_name, last_name, email, student_class, is_verified, is_activate 
            FROM 
                eduapp.msa_registerd_student
            ORDER BY ID DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()

        students = []
        for row in rows:
            students.append({
                "ID": row[0],
                "student_id": row[1],
                "first_name": row[2],
                "middle_name": row[3],
                "last_name": row[4],
                "email": row[5],
                "student_class": row[6],
                "is_verified": bool(row[7]),
                "is_active": bool(row[8])
            })

        return Response(students, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error fetching student list: {e}")
        return Response({"error": "Could not retrieve students."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verified_student_list(request):
    try:
        cursor = connection.cursor()
        sql = """
            SELECT 
                ID, student_id, first_name, middle_name, last_name, email, student_class, is_verified, is_activate 
            FROM 
                eduapp.msa_registerd_student
                WHERE is_verified = 1
            ORDER BY ID DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()

        students = []
        for row in rows:
            students.append({
                "ID": row[0],
                "student_id": row[1],
                "first_name": row[2],
                "middle_name": row[3],
                "last_name": row[4],
                "email": row[5],
                "student_class": row[6],
                "is_verified": bool(row[7]),
                "is_active": bool(row[8])
            })

        return Response(students, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error fetching student list: {e}")
        return Response({"error": "Could not retrieve students."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_detail_by_id(request):
    student_id = request.data.get("student_id")
    if not student_id:
        return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()
        sql = """
            SELECT 
                ID, student_id, first_name, middle_name, last_name, email,
                contact_number_1, contact_number_2, student_class,
                school_or_college_name, board_or_university_name,
                address, city, district, state, pin,
                is_verified, is_active, date_of_birth
            FROM 
                eduapp.msa_registerd_student
            WHERE ID = %s
        """
        cursor.execute(sql, [student_id])
        row = cursor.fetchone()
        cursor.close()

        if not row:
            return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        student = {
            "ID": row[0],
            "student_id": row[1],
            "first_name": row[2],
            "middle_name": row[3],
            "last_name": row[4],
            "email": row[5],
            "contact_number_1": row[6],
            "contact_number_2": row[7],
            "student_class": row[8],
            "school_or_college_name": row[9],
            "board_or_university_name": row[10],
            "address": row[11],
            "city": row[12],
            "district": row[13],
            "state": row[14],
            "pin": row[15],
            "is_verified": bool(row[16]),
            "is_active": bool(row[17]),
            "date_of_birth": row[18].strftime("%Y-%m-%d") if row[18] else None
        }

        return Response(student, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error fetching student detail: {e}")
        return Response({"error": "Could not retrieve student details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    
