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
def student_confirm_otp(request):
    print("Confirm OTP called")
    email = request.data.get("email")
    otp = request.data.get("otp")
    print(  email)
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

        ## Step 3: Register student in msa_student_credentials using serializer
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

        ## Step 4: Generate JWT and respond
        tokens = generate_jwt_for_student(student)

        return Response({
            "message": "Student registered and verified successfully.",
            "student_id": student_db_id,
            "username": email,
            # **tokens
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to complete OTP confirmation and registration."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def student_register_request_otp(request):
#     #  create a basic pythom fumction for add data to database and send otp to email before add data verify email existence I donott want to use serializer and model for this function
#     email = request.data.get("email")
#     if not email:
#         return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
#     print(f"email {email}")
#     otp = generate_otp()
#     print(otp)
#     data = {
#         "email": email,
#         "otp": otp,
#         "first_name": request.data.get("first_name"),
#         "middle_name": request.data.get("middle_name"),
#         "last_name": request.data.get("last_name"),
#         "date_of_birth": request.data.get("date_of_birth"),
#         "contact_number_1": request.data.get("contact_number_1"),
#         "contact_number_2": request.data.get("contact_number_2"),
#         "student_class": request.data.get("student_class"),
#         "school_or_college_name": request.data.get("school_or_college_name"),
#         "board_or_university_name": request.data.get("board_or_university_name"),
#         "address": request.data.get("address"),
#         "city": request.data.get("city"),
#         "district": request.data.get("district"),
#         "state": request.data.get("state"),
#         "pin": request.data.get("pin"),
#         "student_photo_path": request.data.get("student_photo")
#     }

#     # sql check if email already exists
#     # sql = f"""INSERT INTO eduapp.msa_registerd_student (first_name, middle_name, last_name, date_of_birth, contact_number_1, contact_number_2, student_class, school_or_college_name, board_or_university_name, address, city, district, state, pin, notes, email)
#     #           VALUES ('{data['first_name']}', '{data['middle_name']}', '{data['last_name']}', '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}', '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}', '{data['address']}', '{data['city']}', '{data['district']}', '{data['state']}', '{data['pin']}',  '{email}')"""
    
# #     sql = f"""
# #     INSERT INTO eduapp.msa_registerd_student (
# #         first_name, middle_name, last_name, date_of_birth,
# #         contact_number_1, contact_number_2, student_class,
# #         school_or_college_name, board_or_university_name,
# #         address, city, district, state, pin, notes, email,student_type, student_photo_path
# #     ) VALUES (
# #         '{data['first_name']}', '{data['middle_name']}', '{data['last_name']}',
# #         '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}',
# #         '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}',
# #         '{data['address']}', '{data['city']}', '{data['district']}',
# #         '{data['state']}', '{data['pin']}', '{data.get('notes', '')}', '{email}', 'discontinue', '{data.get('student_photo')}'
# #     );
# # ELSE
# #     -- Optional: you can raise a signal or do something else
# #     SELECT 'Email already exists' AS message;
# # END IF;"""
#     sql =f"""
#     INSERT INTO eduapp.msa_registerd_student (
#     first_name, middle_name, last_name, date_of_birth,
#     contact_number_1, contact_number_2, student_class,
#     school_or_college_name, board_or_university_name,
#     address, city, district, state, pin, notes, email, student_type, student_photo_path
# )
# SELECT * FROM (
#     SELECT
#         '{data['first_name']}', '{data['middle_name']}', '{data['last_name']}',
#         '{data['date_of_birth']}', '{data['contact_number_1']}', '{data['contact_number_2']}',
#         '{data['student_class']}', '{data['school_or_college_name']}', '{data['board_or_university_name']}',
#         '{data['address']}', '{data['city']}', '{data['district']}',
#         '{data['state']}', '{data['pin']}', '{data.get('notes')}', '{email}', 'discontinue', '{data.get('student_photo_path')}'
# ) AS tmp
# WHERE NOT EXISTS (
#     SELECT 1 FROM eduapp.msa_registerd_student WHERE email = '{email}'
# );

#     """
#     print(sql)
#     try:
#         cursor = connection.cursor()
#         cursor.execute(sql)
#         # cursor.execute(sql, params)
#         connection.commit()
#         cursor.close()
#         # Send OTP email
#         otp_data = {
#             "otp": otp,
#             "data": data
#         }
#         cache.set(f"student_otp_{email}", otp_data, timeout=OTP_EXPIRY_MINUTES * 60)  # Cache for 10 minutes
#         send_otp_email(email, otp)  
#         return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
#     except Exception as e:  
#         print(f"Database error: {e}")
#         return Response({"error": "Failed to register student."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# @api_view(['POST'])
# def student_register_request_otp(request):
#     email = request.data.get("email")
#     if not email:
#         return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Generate OTP
#     otp = generate_otp()

#     # Get all fields
#     fields = {
#         "first_name": request.data.get("first_name", ""),
#         "middle_name": request.data.get("middle_name", ""),
#         "last_name": request.data.get("last_name", ""),
#         "date_of_birth": request.data.get("date_of_birth", ""),
#         "contact_number_1": request.data.get("contact_number_1", ""),
#         "contact_number_2": request.data.get("contact_number_2", ""),
#         "student_class": request.data.get("student_class", ""),
#         "school_or_college_name": request.data.get("school_or_college_name", ""),
#         "board_or_university_name": request.data.get("board_or_university_name", ""),
#         "address": request.data.get("address", ""),
#         "city": request.data.get("city", ""),
#         "district": request.data.get("district", ""),
#         "state": request.data.get("state", ""),
#         "pin": request.data.get("pin", ""),
#         "notes": request.data.get("notes", ""),
#         "email": email,
#         "student_type": "discontinue",
#         "student_photo_path": request.data.get("student_photo_path", ""),
#     }
#     print(request.data.get("contact_number_1", ""))
#     sql = """
#     INSERT INTO eduapp.msa_registerd_student (
#         first_name, middle_name, last_name, date_of_birth,
#         contact_number_1, contact_number_2, student_class,
#         school_or_college_name, board_or_university_name,
#         address, city, district, state, pin, notes,
#         email, student_type, student_photo_path
#     )
#     SELECT * FROM (
#         SELECT %s AS first_name,
#                %s AS middle_name,
#                %s AS last_name,
#                %s AS date_of_birth,
#                %s AS contact_number_1,
#                %s AS contact_number_2,
#                %s AS student_class,
#                %s AS school_or_college_name,
#                %s AS board_or_university_name,
#                %s AS address,
#                %s AS city,
#                %s AS district,
#                %s AS state,
#                %s AS pin,
#                %s AS notes,
#                %s AS email,
#                %s AS student_type,
#                %s AS student_photo_path
#     ) AS tmp
#     WHERE NOT EXISTS (
#         SELECT 1 FROM eduapp.msa_registerd_student WHERE email = %s
#     );
#     """

#     print(sql)

#     params = list(fields.values()) + [email]

#     try:
#         cursor = connection.cursor()
#         cursor.execute(sql, params)
#         connection.commit()
#         cursor.close()

#         # Cache OTP
#         otp_data = {
#             "otp": otp,
#             "data": fields
#         }
#         cache.set(f"student_otp_{email}", otp_data, timeout=OTP_EXPIRY_MINUTES * 60)

#         # Send OTP
#         send_otp_email(email, otp)

#         return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f"Database error: {e}")
#         return Response({"error": "Failed to register student."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def student_register_request_otp(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    # Check if email already exists in the database
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM eduapp.msa_registerd_student WHERE email = %s", [email])
    if cursor.fetchone():
        return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)
    cursor.close()

    otp = generate_otp()

    fields = {
        "first_name": request.data.get("first_name", ""),
        "middle_name": request.data.get("middle_name", ""),
        "last_name": request.data.get("last_name", ""),
        "date_of_birth": request.data.get("date_of_birth", ""),
        "contact_number_1": request.data.get("contact_number_1", ""),
        "contact_number_2": request.data.get("contact_number_2", ""),
        "student_class": request.data.get("student_class", ""),
        "school_or_college_name": request.data.get("school_or_college_name", ""),
        "board_or_university_name": request.data.get("board_or_university_name", ""),
        "address": request.data.get("address", ""),
        "city": request.data.get("city", ""),
        "district": request.data.get("district", ""),
        "state": request.data.get("state", ""),
        "pin": request.data.get("pin", ""),
        "notes": request.data.get("notes", ""),
        "email": email,
        "student_type": "discontinue",
        "student_photo_path": request.data.get("student_photo_path", ""),
    }

    # Save OTP + student data in cache
    cache.set(f"student_otp_{email}", {
        "otp": otp,
        "data": fields
    }, timeout=OTP_EXPIRY_MINUTES * 60)

    send_otp_email(email, otp)

    return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def student_register_verify_otp(request):
    email = request.data.get("email")
    input_otp = request.data.get("otp")

    if not email or not input_otp:
        return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    cached = cache.get(f"student_otp_{email}")
    if not cached:
        return Response({"error": "OTP expired or not requested."}, status=status.HTTP_400_BAD_REQUEST)

    if cached["otp"] != input_otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

    fields = cached["data"]
    sql = """
        INSERT INTO eduapp.msa_registerd_student (
            first_name, middle_name, last_name, date_of_birth,
            contact_number_1, contact_number_2, student_class,
            school_or_college_name, board_or_university_name,
            address, city, district, state, pin, notes,
            email, student_type, student_photo_path, is_verified 
        )
        SELECT * FROM (
            SELECT %s AS first_name,
                   %s AS middle_name,
                   %s AS last_name,
                   %s AS date_of_birth,
                   %s AS contact_number_1,
                   %s AS contact_number_2,
                   %s AS student_class,
                   %s AS school_or_college_name,
                   %s AS board_or_university_name,
                   %s AS address,
                   %s AS city,
                   %s AS district,
                   %s AS state,
                   %s AS pin,
                   %s AS notes,
                   %s AS email,
                   %s AS student_type,
                   %s AS student_photo_path,
                   1
        ) AS tmp
        WHERE NOT EXISTS (
            SELECT 1 FROM eduapp.msa_registerd_student WHERE email = %s
        );
    """

    params = list(fields.values()) + [email]

    try:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        cursor.close()

        # Clear the OTP cache after success
        cache.delete(f"student_otp_{email}")

        return Response({"message": "Registration successful."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Database error: {e}")
        return Response({"error": "Failed to register student."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def generate_jwt_for_student(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }





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
                ID, student_id, first_name, middle_name, last_name, contact_number_1, email, student_class, student_photo_path, is_verified, is_activate 
            FROM 
                eduapp.msa_registerd_student
            ORDER BY ID DESC
        """
        print(sql)
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
                "contact_number_1": row[5],
                "email": row[6],
                "student_class": row[7],
                "student_photo_path": row[8],
                "is_verified": bool(row[9]),
                "is_active": bool(row[9])
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
                ID, student_id, first_name, middle_name, last_name, email, student_class,student_photo_path, is_verified, is_activate 
            FROM 
                eduapp.msa_registerd_student
                WHERE is_verified = 1
            ORDER BY ID DESC
        """
        print(sql)
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
                "student_photo_path": row[7],
                "is_verified": bool(row[8]),
                "is_active": bool(row[9])
            })

        return Response(students, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error fetching student list: {e}")
        return Response({"error": "Could not retrieve students."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def student_detail_by_id(request):
#     student_id = request.data.get("student_id")
#     if not student_id:
#         return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         cursor = connection.cursor()
#         sql = f"""
#             SELECT
#                 ID, student_id, first_name, middle_name, last_name, email,
#                 contact_number_1, contact_number_2, student_class,
#                 school_or_college_name, board_or_university_name,
#                 address, city, district, state, pin, notes,
#                 is_verified, is_activate, date_of_birth, student_photo_path
#             FROM
#                 eduapp.msa_registerd_student
#             WHERE ID = {student_id}
#         """
#         print(sql)
#         cursor.execute(sql, [student_id])
#         row = cursor.fetchone()
#         cursor.close()

#         if not row:
#             return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

#         student = {
#             "ID": row[0],
#             "student_id": row[1],
#             "first_name": row[2],
#             "middle_name": row[3],
#             "last_name": row[4],
#             "email": row[5],
#             "contact_number_1": row[6],
#             "contact_number_2": row[7],
#             "student_class": row[8],
#             "school_or_college_name": row[9],
#             "board_or_university_name": row[10],
#             "address": row[11],
#             "city": row[12],
#             "district": row[13],
#             "state": row[14],
#             "pin": row[15],
#             "is_verified": bool(row[16]),
#             "is_active": bool(row[17]),
#             "date_of_birth": row[18].strftime("%Y-%m-%d") if row[18] else None,
#             "student_photo_path": row[19] if row[19] else None
#         }

#         return Response(student, status=status.HTTP_200_OK)

#     except Exception as e:
#         print(f"Error fetching student detail: {e}")
#         return Response({"error": "Could not retrieve student details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
                address, city, district, state, pin, notes,
                is_verified, is_activate, date_of_birth, student_photo_path,batch_id
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
            "notes": row[16],
            "is_verified": bool(row[17]),
            "is_active": bool(row[18]),
            "date_of_birth": row[19].strftime("%Y-%m-%d") if row[19] else None,
            "student_photo_path": row[20] if row[20] else None,
            "batch_id": row[21] 

        }

        return Response(student, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error fetching student detail: {e}")
        return Response({"error": "Could not retrieve student details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])  # You can change to PUT if preferred
@permission_classes([IsAuthenticated])
def update_student_detail(request):
    student_id = request.data.get("student_id")
    if not student_id:
        return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        fields = {
            "first_name": request.data.get("first_name", ""),
            "middle_name": request.data.get("middle_name", ""),
            "last_name": request.data.get("last_name", ""),
            "email": request.data.get("email", ""),
            "contact_number_1": request.data.get("contact_number_1", ""),
            "contact_number_2": request.data.get("contact_number_2", ""),
            "student_class": request.data.get("student_class", ""),
            "school_or_college_name": request.data.get("school_or_college_name", ""),
            "board_or_university_name": request.data.get("board_or_university_name", ""),
            "address": request.data.get("address", ""),
            "city": request.data.get("city", ""),
            "district": request.data.get("district", ""),
            "state": request.data.get("state", ""),
            "pin": request.data.get("pin", ""),
            "notes": request.data.get("notes", ""),
            "is_verified": int(request.data.get("is_verified", False)),
            "is_activate": int(request.data.get("is_activate", False)),
            "date_of_birth": request.data.get("date_of_birth", None),
            "student_photo_path": request.data.get("student_photo_path", None),
            "batch_id": request.data.get("batch_id", None),
        }

        sql = """
            UPDATE eduapp.msa_registerd_student
            SET
                first_name = %s,
                middle_name = %s,
                last_name = %s,
                email = %s,
                contact_number_1 = %s,
                contact_number_2 = %s,
                student_class = %s,
                school_or_college_name = %s,
                board_or_university_name = %s,
                address = %s,
                city = %s,
                district = %s,
                state = %s,
                pin = %s,
                notes = %s,
                is_verified = %s,
                is_activate = %s,
                date_of_birth = %s,
                student_photo_path = %s,
                batch_id = %s
            WHERE ID = %s
        """

        cursor = connection.cursor()
        cursor.execute(sql, [
            fields["first_name"],
            fields["middle_name"],
            fields["last_name"],
            fields["email"],
            fields["contact_number_1"],
            fields["contact_number_2"],
            fields["student_class"],
            fields["school_or_college_name"],
            fields["board_or_university_name"],
            fields["address"],
            fields["city"],
            fields["district"],
            fields["state"],
            fields["pin"],
            fields["notes"],
            fields["is_verified"],
            fields["is_activate"],
            fields["date_of_birth"],
            fields["student_photo_path"],
            fields["batch_id"],
            student_id
        ])
        connection.commit()
        cursor.close()

        return Response({"message": "Student details updated successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error updating student detail: {e}")
        return Response({"error": "Failed to update student details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def request_student_login_otp(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT ID FROM eduapp.msa_registerd_student WHERE email = %s", [email])
        student = cursor.fetchone()
        if not student:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()
        timestamp = timezone.now()

        # Save OTP + student data in cache
        cache.set(f"student_otp_{email}", {
            "otp": otp,
        }, timeout=OTP_EXPIRY_MINUTES * 60)

        send_otp_email(email, otp)

        # Save OTP in a temporary table (you must create this table)
        cursor.execute("""
            INSERT INTO eduapp.student_otp_log (email, otp_code, created_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE otp_code = VALUES(otp_code), created_at = VALUES(created_at)
        """, [email, otp, timestamp])
        connection.commit()
        cursor.close()

        # TODO: Send OTP to email (integrate your email logic)
        print(f"OTP for {email}: {otp}")


        return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error requesting OTP: {e}")
        return Response({"error": "Failed to send OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def verify_student_login_otp(request):
    email = request.data.get("email")
    otp = request.data.get("otp")

    if not email or not otp:
        return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()

        # Verify OTP from the temp log table
        cursor.execute("""
            SELECT created_at FROM eduapp.student_otp_log
            WHERE email = %s AND otp_code = %s
        """, [email, otp])
        row = cursor.fetchone()

        if not row:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_401_UNAUTHORIZED)

        # You may optionally check timestamp validity here

        # Get student ID
        cursor.execute("""SELECT ID, 
                       first_name, middle_name, last_name, date_of_birth,
            contact_number_1, contact_number_2,
            student_class, batch_id, is_activate,
            school_or_college_name, board_or_university_name,
            address, city, district, state, pin, 
            email, student_type, student_photo_path
                       FROM eduapp.msa_registerd_student WHERE email = %s""", [email])
        
        student = cursor.fetchone()
        if not student:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        
        student_data = {
    "ID": student[0],
    "first_name": student[1],
    "middle_name": student[2],
    "last_name": student[3],
    "date_of_birth": student[4].strftime("%Y-%m-%d") if student[4] else None,
    "contact_number_1": student[5],
    "contact_number_2": student[6],
    "student_class": student[7],
    "batch_id": student[8],
    "is_activate": student[9],
    "school_or_college_name": student[10],
    "board_or_university_name": student[11],
    "address": student[12],
    "city": student[13],
    "district": student[14],
    "state": student[15],
    "pin": student[16],
    "email": student[17],
    "student_type": student[18],
    "student_photo_path": student[19]  # ✅ last valid index
}


        # Fake user object
        class StudentUser:
            def __init__(self):
                self.id = student_data["ID"]
            @property
            def is_authenticated(self):
                return True

        student_user = StudentUser()

        refresh = RefreshToken.for_user(student_user)

        # Optionally delete used OTP
        cursor.execute("DELETE FROM eduapp.student_otp_log WHERE email = %s", [email])
        connection.commit()
        cursor.close()

        return Response({
    "access": str(refresh.access_token),
    "refresh": str(refresh),
    "student_id": student_data["ID"],
    "first_name": student_data["first_name"],   
    "middle_name": student_data["middle_name"],
    "last_name": student_data["last_name"],
    "date_of_birth": student_data["date_of_birth"],
    "contact_number_1": student_data["contact_number_1"],
    "contact_number_2": student_data["contact_number_2"],
    "student_class": student_data["student_class"],
    "batch_id": student_data["batch_id"],
    "is_activate": student_data["is_activate"],
    "school_or_college_name": student_data["school_or_college_name"],
    "board_or_university_name": student_data["board_or_university_name"],
    "address": student_data["address"],
    "city": student_data["city"],
    "district": student_data["district"],
    "state": student_data["state"],
    "pin": student_data["pin"],
    "email": student_data["email"],
    "student_type": student_data["student_type"],
    "student_photo_path": student_data["student_photo_path"]
}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"OTP verification error: {e}")
        return Response({"error": "OTP verification failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
