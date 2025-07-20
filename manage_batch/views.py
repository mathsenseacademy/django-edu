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
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_batch(request):
    input_data = JSONParser().parse(request)
    batch_name = input_data.get('batch_name')
    description = input_data.get('description', '')
    course_id = input_data.get('course_id')
    schedules = input_data.get('schedules', [])

    if not batch_name or not course_id or not schedules:
        return Response({"error": "Batch name, course_id and schedules are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()

        # Insert into msa_batch
        cursor.execute(
            """
            INSERT INTO eduapp.msa_batch (batch_name, description, course_id, is_activate)
            VALUES (%s, %s, %s, 1)
            """,
            [batch_name, description, course_id]
        )
        batch_id = cursor.lastrowid

        # Insert batch schedules
        for sched in schedules:
            weekday = sched.get('weekday')
            start_time = sched.get('start_time')
            end_time = sched.get('end_time')
            if not weekday or not start_time:
                continue
            cursor.execute(
                """
                INSERT INTO eduapp.msa_batch_schedule (batch_id, weekday, start_time, end_time)
                VALUES (%s, %s, %s, %s)
                """,
                [batch_id, weekday, start_time, end_time]
            )

        connection.commit()
        cursor.close()
        return Response({"message": "Batch created successfully under course"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to create batch"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_batches_with_schedule(request):
    try:
        cursor = connection.cursor()

        # Step 1: Fetch all batches with course info
        cursor.execute("""
            SELECT 
                b.id AS batch_id,
                b.batch_name,
                b.description,
                c.course_name
            FROM 
                eduapp.msa_batch b
            LEFT JOIN 
                eduapp.msa_course c ON b.course_id = c.id
            ORDER BY 
                b.id
        """)
        batch_rows = cursor.fetchall()

        # Convert to dict list
        batch_list = []
        for row in batch_rows:
            batch_list.append({
                "batch_id": row[0],
                "batch_name": row[1],
                "description": row[2],
                "course_name": row[3],
                "schedules": []
            })

        # Step 2: Fetch all schedules
        batch_ids = [b["batch_id"] for b in batch_list]
        if batch_ids:
            format_strings = ','.join(['%s'] * len(batch_ids))
            cursor.execute(f"""
                SELECT 
                    batch_id, weekday, start_time, end_time
                FROM 
                    eduapp.msa_batch_schedule
                WHERE 
                    batch_id IN ({format_strings})
                ORDER BY 
                    batch_id, FIELD(weekday, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), start_time
            """, batch_ids)
            schedule_rows = cursor.fetchall()

            # Map schedules to batches
            batch_map = {b["batch_id"]: b for b in batch_list}
            for row in schedule_rows:
                batch_id, weekday, start_time, end_time = row
                schedule = {
                    "weekday": weekday,
                    "start_time": str(start_time),
                    "end_time": str(end_time) if end_time else None
                }
                batch_map[batch_id]["schedules"].append(schedule)

        return Response(batch_list, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to fetch batch data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_detail_by_id(request):
    batch_id = request.data.get('batch_id')
    if not batch_id:
        return Response({"error": "Batch ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()

        # Fetch the batch details
        cursor.execute("""
            SELECT 
                b.id AS batch_id,
                b.batch_name,
                b.description,
                c.course_name
            FROM 
                eduapp.msa_batch b
            LEFT JOIN 
                eduapp.msa_course c ON b.course_id = c.id
            WHERE 
                b.id = %s
        """, [batch_id])
        batch_row = cursor.fetchone()

        if not batch_row:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        result = {
            "batch_id": batch_row[0],
            "batch_name": batch_row[1],
            "description": batch_row[2],
            "course_name": batch_row[3],
            "schedules": [],
            "fees": []
        }

        # Fetch schedules for the batch
        cursor.execute("""
            SELECT 
                weekday, start_time, end_time
            FROM 
                eduapp.msa_batch_schedule
            WHERE 
                batch_id = %s
            ORDER BY 
                FIELD(weekday, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'), start_time
        """, [batch_id])
        schedule_rows = cursor.fetchall()

        for row in schedule_rows:
            result["schedules"].append({
                "weekday": row[0],
                "start_time": str(row[1]),
                "end_time": str(row[2]) if row[2] else None
            })
        
        # Fetch fees for the batch
        cursor.execute("""
            SELECT fee_title, amount, due_date, fee_type
            FROM eduapp.msa_batch_fee
            WHERE batch_id = %s
        """, [batch_id])
        fee_rows = cursor.fetchall()
        for f in fee_rows:
            result["fees"].append({
                "fee_title": f[0],
                "amount": str(f[1]),
                "due_date": str(f[2]) if f[2] else None,
                "fee_type": f[3]
            })

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to retrieve batch details."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_batch(request):
    input_data = request.data
    batch_id = input_data.get('batch_id')
    batch_name = input_data.get('batch_name')
    description = input_data.get('description', '')
    course_id = input_data.get('course_id')
    schedules = input_data.get('schedules', [])

    if not batch_id or not batch_name or not course_id:
        return Response({"error": "batch_id, batch_name and course_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()

        # 1. Update batch table
        cursor.execute("""
            UPDATE eduapp.msa_batch
            SET batch_name = %s, description = %s, course_id = %s
            WHERE id = %s
        """, [batch_name, description, course_id, batch_id])

        # 2. Delete existing schedule entries for this batch
        cursor.execute("""
            DELETE FROM eduapp.msa_batch_schedule
            WHERE batch_id = %s
        """, [batch_id])

        # 3. Re-insert schedule
        for sched in schedules:
            weekday = sched.get('weekday')
            start_time = sched.get('start_time')
            end_time = sched.get('end_time')

            if not weekday or not start_time:
                continue

            cursor.execute("""
                INSERT INTO eduapp.msa_batch_schedule (batch_id, weekday, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, [batch_id, weekday, start_time, end_time])

        connection.commit()
        cursor.close()

        return Response({"message": "Batch updated successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to update batch."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_batch_fee(request):
    data = request.data
    batch_id = data.get("batch_id")
    title = data.get("fee_title")
    amount = data.get("amount")
    due_date = data.get("due_date")
    fee_type = data.get("fee_type", "one-time")

    if not batch_id or not title or not amount:
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO eduapp.msa_batch_fee (batch_id, fee_title, amount, due_date, fee_type)
            VALUES (%s, %s, %s, %s, %s)
        """, [batch_id, title, amount, due_date, fee_type])
        connection.commit()
        cursor.close()
        return Response({"message": "Batch fee added."}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to add batch fee."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_batch_fee(request):
    try:
        cursor = connection.cursor()
        cursor.execute("""  
            SELECT  
                bf.id AS batch_fee_id,
                bf.fee_title,
                bf.amount,
                bf.due_date,
                bf.fee_type,
                b.batch_name,
                b.id AS batch_id
            FROM 
                eduapp.msa_batch_fee bf
            JOIN eduapp.msa_batch b ON bf.batch_id = b.id
        """)

        batch_fees = cursor.fetchall()
        

        # Convert to dict list
        batch_fee_list = []
        for row in batch_fees:
            batch_fee_list.append({
                "batch_fee_id": row[0],
                "fee_title": row[1],
                "amount": row[2],
                "due_date": row[3],
                "fee_type": row[4],
                "batch_name": row[5],
                "batch_id": row[6]
            })
        return Response(batch_fees, status= status.HTTP_200_OK)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Database connection failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_fee_by_id(request):
    if request.method == 'POST':
        try:
            batch_fee_id = request.data.get("batch_fee_id")
            if not batch_fee_id:
                return Response({"error": "Missing batch_fee_id."}, status=status.HTTP_400_BAD_REQUEST)

            cursor = connection.cursor()
            cursor.execute("""  
                SELECT  
                    bf.id AS batch_fee_id,
                    bf.fee_title,
                    bf.amount,
                    bf.due_date,
                    bf.fee_type,
                    b.batch_name,
                    b.id AS batch_id
                FROM 
                    eduapp.msa_batch_fee bf
                JOIN eduapp.msa_batch b ON bf.batch_id = b.id
            """)

            batch_fees = cursor.fetchall()
            return Response(batch_fees, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "Database connection failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'PUT':
        try:
            data = request.data
            batch_fee_id = data.get("batch_fee_id")
            fee_title = data.get("fee_title")
            amount = data.get("amount")
            due_date = data.get("due_date")
            fee_type = data.get("fee_type", "one-time")

            if not all([batch_fee_id, fee_title, amount, due_date]):
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            cursor = connection.cursor()
            cursor.execute("""
                UPDATE eduapp.msa_batch_fee
                SET fee_title = %s, amount = %s, due_date = %s, fee_type = %s
                WHERE id = %s
            """, (fee_title, amount, due_date, fee_type, batch_fee_id))
            connection.commit()
            return Response({"message": "Batch fee updated successfully."}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "Database connection failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# recived payment or add data msa_student_batch_fee
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_student_fee_payment(request):
    data = request.data

    student_id = data.get("student_id")
    batch_fee_id = data.get("batch_fee_id") 
    payment_status = data.get("payment_status", "paid")
    payment_date = data.get("payment_date", timezone.now())
    transaction_id = data.get("transaction_id", None)
    if not student_id or not batch_fee_id:
        return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO eduapp.msa_student_batch_fee (student_id, batch_fee_id, payment_status, payment_date, transaction_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (student_id, batch_fee_id, payment_status, payment_date, transaction_id))
        connection.commit()
        return Response({"message": "Payment recorded successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# studentwise fee status by batch
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_fee_status_by_batch(request):
    batch_id = request.data.get("batch_id")
    if not batch_id:
        return Response({"error": "Batch ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cursor = connection.cursor()

        # Step 1: Get students mapped to this batch
        cursor.execute("""
            SELECT student.id, student.first_name, student.last_name
            FROM eduapp.msa_registerd_student student
            JOIN eduapp.msa_batch batch ON student.batch_id = batch.ID            

            WHERE batch.ID = %s
        """, [batch_id])
        students = cursor.fetchall()

        # Step 2: Get all fees assigned to this batch
        cursor.execute("""
            SELECT id, fee_title, amount
            FROM eduapp.msa_batch_fee
            WHERE batch_id = %s
        """, [batch_id])
        fees = cursor.fetchall()

        # Step 3: Get existing fee payments for these students
        fee_ids = [f[0] for f in fees]
        if fee_ids:
            format_strings = ','.join(['%s'] * len(fee_ids))
            cursor.execute(f"""
                SELECT student_id, batch_fee_id, payment_status, payment_date, transaction_id
                FROM eduapp.msa_student_batch_fee
                WHERE batch_fee_id IN ({format_strings})
            """, fee_ids)
            print(f"""SELECT student_id, batch_fee_id, payment_status, payment_date, transaction_id
                FROM eduapp.msa_student_batch_fee
                WHERE batch_fee_id IN ({format_strings})""")
            payment_rows = cursor.fetchall()
        else:
            payment_rows = []

        if payment_rows is None:
            return Response({"message": "No fee payments found for this batch."}, status=status.HTTP_404_NOT_FOUND)     
        # Step 4: Create lookup map
        payment_map = {}
        for row in payment_rows:
            student_id, fee_id, status, pay_date, txn_id = row
            key = (student_id, fee_id)
            payment_map[key] = {
                "status": status,
                "payment_date": str(pay_date) if pay_date else None,
                "transaction_id": txn_id
            }

        # Step 5: Assemble result
        result = []
        for student in students:
            student_id, first_name, last_name = student
            fee_data = []

            for fee in fees:
                fee_id, title, amount = fee
                key = (student_id, fee_id)
                payment = payment_map.get(key, {
                    "status": "unpaid",
                    "payment_date": None,
                    "transaction_id": None
                })

                fee_data.append({
                    "fee_title": title,
                    "amount": str(amount),
                    "payment_status": payment["status"],
                    "payment_date": payment["payment_date"],
                    "transaction_id": payment["transaction_id"]
                })

            result.append({
                "student_id": student_id,
                "name": f"{first_name} {last_name}",
                "fees": fee_data
            })

        return Response(result, status=200)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=500)

