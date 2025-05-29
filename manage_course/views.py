from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

from student_user.models import Student
from student_user.serializers import StudentSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batches(request):
    input_data =  JSONParser().parse(request)
    batchesname = input_data.get('name')
    class_level = input_data.get('class_level')
    category = input_data.get('category')
    focus_area = input_data.get('focus_area')

    sql = f"""INSERT INTO `eduapp`.`msa_batches` (`name`, `class_level`, `category`, `focus_area`, `is_activate`)
                VALUES
                ('{batchesname}', '{class_level}', '{category}', '{focus_area}', 1);
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return Response({"message": "Batch created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def editbatchs(request):
    input_data =  JSONParser().parse(request)
    batchesname = input_data.get('name')
    class_level = input_data.get('class_level')
    category = input_data.get('category')
    focus_area = input_data.get('focus_area')
    isActive = input_data.get('is_active')
    id = input_data.get('id')
    if not id:
        return Response({"error": "ID is required to update a batch"}, status=status.HTTP_400_BAD_REQUEST)
    updatesql = ""

    if batchesname:
        updatesql += f" SET name = '{batchesname}'"
    if class_level:
        updatesql += f", class_level = '{class_level}'" 
    if category:   
        updatesql += f", category = '{category}'"
    if focus_area:        
        updatesql += f", focus_area = '{focus_area}'"
    if isActive:        
        updatesql += f", is_activate = {isActive}"
    
    updatesql += f" WHERE ID = {id}"
    if not updatesql.startswith(" SET "):
        return Response({"error": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)
    cursor = connection.cursor()
    cursor.execute(updatesql)

    connection.commit()
    cursor.close()
    return Response({"message": "Question updated successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createcourses(request):
    input_data =  JSONParser().parse(request)
    batch_ID = input_data.get('batch_ID')
    short_description = input_data.get('short_description')
    description = input_data.get('description')

    sql = f"""INSERT INTO `eduapp`.`msa_courses` (`batch_ID`, `short_description`, `description`, `is_activate`)
                VALUES
                ('{batch_ID}', '{short_description}', '{description}', 1);
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def editcourses(request):
    input_data =  JSONParser().parse(request)
    batch_ID = input_data.get('batch_ID')
    short_description = input_data.get('short_description')
    description = input_data.get('description')
    isActive = input_data.get('is_active')
    id = input_data.get('id')
    if not id:
        return Response({"error": "ID is required to update a course"}, status=status.HTTP_400_BAD_REQUEST)
    updatesql = ""

    if batch_ID:
        updatesql += f" SET batch_ID = '{batch_ID}'"
    if short_description:
        updatesql += f", short_description = '{short_description}'" 
    if description:   
        updatesql += f", description = '{description}'"
    if isActive:        
        updatesql += f", is_activate = {isActive}"

    updatesql += f" WHERE ID = {id}"
    if not updatesql.startswith(" SET "):
        return Response({"error": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)
    cursor = connection.cursor()
    cursor.execute(updatesql)

    connection.commit()
    cursor.close()
    return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)