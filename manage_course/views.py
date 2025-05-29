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
def create_course(request):
    input_data =  JSONParser().parse(request)
    course_name = input_data.get('course_name')
    class_level = input_data.get('class_level')
    category = input_data.get('category')
    focus_area = input_data.get('focus_area')

    sql = f"""INSERT INTO `eduapp`.`msa_courses` (`course_name`, `class_level`, `category`, `focus_area`, `is_activate`)
                VALUES
                ('{course_name}', '{class_level}', '{category}', '{focus_area}', 1);
        """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_course(request):
    input_data =  JSONParser().parse(request)
    course_name = input_data.get('course_name')
    class_level = input_data.get('class_level')
    category = input_data.get('category')
    focus_area = input_data.get('focus_area')
    isActive = input_data.get('is_active')
    print(isActive)
    id = input_data.get('id')
    if not id:
        return Response({"error": "ID is required to update a course"}, status=status.HTTP_400_BAD_REQUEST)
    updatesql = "UPDATE `eduapp`.`msa_courses` SET"

    if course_name:
        updatesql += f"  course_name = '{course_name}',"
    if class_level:
        updatesql += f" class_level = '{class_level}'," 
    if category:   
        updatesql += f" category = '{category}',"
    if focus_area:        
        updatesql += f", focus_area = '{focus_area}',"
    # if isActive:      
    #     print(isActive)  
    #     updatesql += f" is_activate = {isActive}"
    
    updatesql += f" is_activate = {isActive} WHERE course_ID = {id}"

    print(updatesql)

    # if not updatesql.startswith(" SET "):
    #     return Response({"error": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)
    cursor = connection.cursor()
    cursor.execute(updatesql)

    connection.commit()
    cursor.close()
    return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def show_course_by_id(request):
    input_data =  JSONParser().parse(request)
    sql = f"""SELECT course_ID, course_name, class_level, category, focus_area FROM eduapp.msa_courses
              WHERE  course_ID = {input_data.get('id')}"""
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active courses found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "course_ID": row[0],
            "course_name": row[1],
            "class_level": row[2],
            "category": row[3],
            "focus_area": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_courses(request):
    sql = "SELECT course_ID, course_name, class_level, category, focus_area FROM eduapp.msa_courses"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active courses found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "course_ID": row[0],
            "course_name": row[1],
            "class_level": row[2],
            "category": row[3],
            "focus_area": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_activate_courses(request):
    sql = "SELECT course_ID, course_name, class_level, category, focus_area FROM eduapp.msa_courses WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active course found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "course_ID": row[0],
            "course_name": row[1],
            "class_level": row[2],
            "category": row[3],
            "focus_area": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def createcourses(request):
#     input_data =  JSONParser().parse(request)
#     batch_ID = input_data.get('batch_ID')
#     short_description = input_data.get('short_description')
#     description = input_data.get('description')

#     sql = f"""INSERT INTO `eduapp`.`msa_courses` (`batch_ID`, `short_description`, `description`, `is_activate`)
#                 VALUES
#                 ('{batch_ID}', '{short_description}', '{description}', 1);
#         """
#     cursor = connection.cursor()
#     cursor.execute(sql)
#     connection.commit()
#     cursor.close()
#     return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def editcourses(request):
#     input_data =  JSONParser().parse(request)
#     batch_ID = input_data.get('batch_ID')
#     short_description = input_data.get('short_description')
#     description = input_data.get('description')
#     isActive = input_data.get('is_active')
#     id = input_data.get('id')
#     if not id:
#         return Response({"error": "ID is required to update a course"}, status=status.HTTP_400_BAD_REQUEST)
#     updatesql = ""

#     if batch_ID:
#         updatesql += f" SET batch_ID = '{batch_ID}'"
#     if short_description:
#         updatesql += f", short_description = '{short_description}'" 
#     if description:   
#         updatesql += f", description = '{description}'"
#     if isActive:        
#         updatesql += f", is_activate = {isActive}"

#     updatesql += f" WHERE ID = {id}"
#     if not updatesql.startswith(" SET "):
#         return Response({"error": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)
#     cursor = connection.cursor()
#     cursor.execute(updatesql)

#     connection.commit()
#     cursor.close()
#     return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)