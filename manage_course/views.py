from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import JSONParser

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_course(request):
    input_data =  JSONParser().parse(request)
    course_name = input_data.get('course_name')
    course_subtitle = input_data.get('course_subtitle')
    course_image_path = input_data.get('course_image_path')
    course_video_path = input_data.get('course_video_path')
    student_id_of_the_week = input_data.get('student_id_of_the_week')
    class_level_id = input_data.get('class_level_id')
    category_id = input_data.get('category_id')
    show_in_forntpage = input_data.get('show_in_forntpage')

    sql = f"""INSERT INTO eduapp.msa_course (`course_name`, `course_subtitle`, `course_image_path`,`course_video_path`, `student_id_of_the_week`, `class_level_id`, `category_id`, `show_in_forntpage`, `is_activate`)
                VALUES
                ('{course_name}','{course_subtitle}', '{course_image_path}', '{course_video_path}', '{student_id_of_the_week}', '{class_level_id}', '{category_id}', '{show_in_forntpage}', 1);
        """
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to add course"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_course(request):
    input_data = JSONParser().parse(request)
    course_name = input_data.get('course_name')
    course_subtitle = input_data.get('course_subtitle')
    course_image_path = input_data.get('course_image_path')
    course_video_path = input_data.get('course_video_path')
    student_id_of_the_week = input_data.get('student_id_of_the_week')
    class_level_id = input_data.get('class_level_id')
    category_id = input_data.get('category_id')
    show_in_forntpage = input_data.get('show_in_forntpage')
    isActive = input_data.get('isActive')
    ID = input_data.get('id')

    if not ID:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    fields = []
    if course_name:
        fields.append(f"course_name = '{course_name}'")
    if course_subtitle:
        fields.append(f"course_subtitle = '{course_subtitle}'")
    if course_image_path:
        fields.append(f"course_image_path = '{course_image_path}'")
    if course_video_path:
        fields.append(f"course_video_path = '{course_video_path}'")
    if student_id_of_the_week:
        fields.append(f"student_id_of_the_week = '{student_id_of_the_week}'")
    if class_level_id:
        fields.append(f"class_level_id = '{class_level_id}'")
    if category_id:
        fields.append(f"category_id = '{category_id}'")
    if show_in_forntpage is not None:
        fields.append(f"show_in_forntpage = '{show_in_forntpage}'")
    if isActive is not None:
        fields.append(f"is_activate = {int(isActive)}")

    if not fields:
        return Response({"error": "No fields provided to update"}, status=status.HTTP_400_BAD_REQUEST)

    # updatesql = f"UPDATE eduapp.msa_courses SET {', '.join(fields)} WHERE ID = {ID};"
    updatesql = f"UPDATE eduapp.msa_course SET {', '.join(fields)} WHERE ID = {ID};"
    print(f"sql: {updatesql}")

    try:
        cursor = connection.cursor()
        cursor.execute(updatesql)
        connection.commit()
        cursor.close()
        return Response({"message": "Course updated successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": "Failed to update course"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def show_course_by_id(request):
    input_data =  JSONParser().parse(request)
    sql = f"""SELECT ID,
    course_name,
    course_subtitle,
    course_image_path,
    course_video_path,
    student_id_of_the_week,
    class_level_id,
    category_id,
    show_in_forntpage
       FROM eduapp.msa_course
              WHERE  ID = {input_data.get('id')}"""
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active courses found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "ID": row[0],
            "course_name": row[1],
            "course_subtitle": row[2],
            "course_image_path": row[3],
            "course_video_path": row[4],
            "student_id_of_the_week": row[5],
            "class_level_id": row[6],
            "category_id": row[7],
            "show_in_forntpage": row[8]
        })

    return Response(batch_list, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_courses(request):
    sql = "SELECT ID, course_name, course_subtitle, course_image_path, course_video_path, student_id_of_the_week, class_level_id, category_id, show_in_forntpage FROM eduapp.msa_course"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active courses found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "ID": row[0],
            "course_name": row[1],
            "class_level": row[2],
            "category": row[3],
            "focus_area": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_activate_courses(request):
    sql = "SELECT ID, course_name, class_level_id, category_id, student_id_of_the_week FROM eduapp.msa_course WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active course found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "ID": row[0],
            "course_name": row[1],
            "class_level": row[2],
            "category": row[3],
            "focus_area": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)


@api_view(['GET'])
def all_courses_show_public(request):
    # sql = "SELECT ID, course_name, course_subtitle, course_image_path FROM eduapp.msa_course WHERE show_in_forntpage = 1"
    sql = """
    SELECT 
    c.ID, 
    c.course_name, 
    c.course_subtitle, 
    c.course_image_path, 
    cl.class_name
FROM 
    eduapp.msa_course c
JOIN 
    eduapp.msa_class_level cl 
    ON c.class_level_id = cl.ID
WHERE 
    c.show_in_forntpage = 1;
"""
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active courses found"}, status=status.HTTP_404_NOT_FOUND)

    batch_list = []
    for row in rows:
        batch_list.append({
            "ID": row[0],
            "course_name": row[1],
            "course_subtitle": row[2],
            "course_image_path": row[3],
            "msa_class_level": row[4]
        })

    return Response(batch_list, status=status.HTTP_200_OK)



@api_view(['POST'])
def courses_detail_show_public(request):
    input_data = JSONParser().parse(request)
    course_id = input_data.get('ID')
    
    if not course_id:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    cursor = connection.cursor()

    # Get main course info with class level name and student details
    sql = f"""
        SELECT 
            c.ID,
            c.course_name,
            c.course_subtitle,
            c.course_image_path,
            c.course_video_path,
            c.class_level_id,
            cl.class_name,
            c.category_id,

            s.ID AS student_id,
            s.first_name,
            s.middle_name,
            s.last_name,
            s.student_photo_path

        FROM eduapp.msa_course AS c
        LEFT JOIN eduapp.msa_class_level AS cl
            ON c.class_level_id = cl.ID AND cl.is_activate = 1
        LEFT JOIN eduapp.msa_registerd_student AS s
            ON c.student_id_of_the_week = s.ID 
            AND s.is_activate = 1 AND s.is_verified = 1
        WHERE c.ID = %s AND c.show_in_forntpage = 1
    """
    cursor.execute(sql, [course_id]) #this id ic course ID
    row = cursor.fetchone()

    if not row:
        cursor.close()
        return Response({"message": "Course not found or not available for public view"}, status=status.HTTP_404_NOT_FOUND)

    course_detail = {
        "course_id": row[0],
        "course_name": row[1],
        "course_subtitle": row[2],
        "course_image_path": row[3],
        "course_video_path": row[4],
        "class_level_id": row[5],
        "class_name": row[6],
        "category_id": row[7],
        "student_of_the_week": {
            "student_id": row[8],
            "first_name": row[9],
            "middle_name": row[10],
            "last_name": row[11],
            "student_photo_path": row[12]
        } if row[8] else None,
        "curriculums": [],
        "classroom_essentials": []
    }

    # Fetch curriculums
    sql_curriculums = """
        SELECT ID, curriculum_name
        FROM eduapp.msa_curriculums
        WHERE course_id = %s AND is_activate = 1
    """
    cursor.execute(sql_curriculums, [course_id])
    curriculum_rows = cursor.fetchall()
    for r in curriculum_rows:
        course_detail["curriculums"].append({
            "curriculum_id": r[0],
            "curriculum_name": r[1]
        })

    # Fetch classroom essentials
    sql_essentials = """
        SELECT ID, classroom_essentials_name, classroom_essentials_description
        FROM eduapp.msa_classroom_essentials
        WHERE course_id = %s AND is_activate = 1
    """
    cursor.execute(sql_essentials, [course_id])
    essentials_rows = cursor.fetchall()
    for r in essentials_rows:
        course_detail["classroom_essentials"].append({
            "classroom_essential_id": r[0],
            "classroom_essentials_name": r[1],
            "classroom_essentials_description": r[2]
        })

    cursor.close()
    return Response(course_detail, status=status.HTTP_200_OK)



# course_curriculum
@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def add_course_curriculum(request):
    if request.method == 'POST':
        input_data = JSONParser().parse(request)
        curriculum_name = input_data.get('curriculum_name')
        course_id = input_data.get('course_id')

        if not curriculum_name or not course_id:
            return Response({"error": "Curriculum name and Course ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        sql = f"""INSERT INTO eduapp.msa_curriculums (curriculum_name, course_id, is_activate)
                  VALUES ('{curriculum_name}', {course_id}, 1)"""
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        return Response({"message": "Curriculum added successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def show_all_curriculums(request):
    sql = "SELECT ID, curriculum_name, course_id, is_activate FROM eduapp.msa_curriculums"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No curriculums found"}, status=status.HTTP_404_NOT_FOUND)

    curriculum_list = []
    for row in rows:
        curriculum_list.append({
            "curriculum_id": row[0],
            "curriculum_name": row[1],
            "ID": row[2],
            "is_activate": row[3]
        })

    return Response(curriculum_list, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def show_curriculum_by_id(request):
    input_data = JSONParser().parse(request)
    curriculum_id = input_data.get('curriculum_id')
    
    if not curriculum_id:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, curriculum_name, course_id, is_activate FROM eduapp.msa_curriculums WHERE ID = {curriculum_id}"
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return Response({"message": "Curriculum not found"}, status=status.HTTP_404_NOT_FOUND)

    curriculum_detail = {
        "curriculum_id": row[0],
        "curriculum_name": row[1],
        "ID": row[2],
        "is_activate": row[3]
    }

    return Response(curriculum_detail, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def edit_curriculum(request):
    input_data = JSONParser().parse(request)
    curriculum_id = input_data.get('curriculum_id')
    curriculum_name = input_data.get('curriculum_name')
    course_id = input_data.get('course_id')
    is_activate = input_data.get('is_activate')

    if not curriculum_id:
        return Response({"error": "Curriculum ID is required to update"}, status=status.HTTP_400_BAD_REQUEST)

    updatesql = "UPDATE eduapp.msa_curriculums SET"

    if curriculum_name:
        updatesql += f" curriculum_name = '{curriculum_name}',"
    if course_id:
        updatesql += f" course_id = {course_id},"
    if is_activate is not None:
        updatesql += f" is_activate = {is_activate}"

    updatesql += f" WHERE ID = {curriculum_id}"

    cursor = connection.cursor()
    cursor.execute(updatesql)
    connection.commit()
    cursor.close()

    return Response({"message": "Curriculum updated successfully"}, status=status.HTTP_200_OK)  

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def show_active_curriculums(request):
    sql = "SELECT ID, curriculum_name, course_id FROM eduapp.msa_curriculums WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active curriculums found"}, status=status.HTTP_404_NOT_FOUND)

    curriculum_list = []
    for row in rows:
        curriculum_list.append({
            "curriculum_id": row[0],
            "curriculum_name": row[1],
            "ID": row[2]
        })

    return Response(curriculum_list, status=status.HTTP_200_OK) 

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def show_active_curriculums_by_course_id(request):
    input_data = JSONParser().parse(request)
    course_id = input_data.get('course_id')
    
    if not course_id:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, curriculum_name FROM eduapp.msa_curriculums WHERE is_activate = 1 AND course_id = {course_id}"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active curriculums found for this course"}, status=status.HTTP_404_NOT_FOUND)

    curriculum_list = []
    for row in rows:
        curriculum_list.append({
            "curriculum_id": row[0],
            "curriculum_name": row[1]
        })

    return Response(curriculum_list, status=status.HTTP_200_OK)

# classroom essentials
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_classroom_essentials(request):
    if request.method == 'POST':
        input_data = JSONParser().parse(request)
        classroom_essentials_name = input_data.get('classroom_essentials_name')
        classroom_essentials_description = input_data.get('classroom_essentials_description')
        course_id= input_data.get('course_id')

        if not classroom_essentials_name or not course_id:
            return Response({"error": "Classroom essentials name and Course ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        sql = f"""INSERT INTO eduapp.msa_classroom_essentials (classroom_essentials_name, classroom_essentials_description, course_id, is_activate)
                  VALUES ('{classroom_essentials_name}', '{classroom_essentials_description}', {course_id}, 1)"""
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        return Response({"message": "Classroom essentials added successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def show_all_classroom_essentials(request):
    sql = "SELECT ID, classroom_essentials_name, classroom_essentials_description, ID, is_activate FROM eduapp.msa_classroom_essentials"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No classroom essentials found"}, status=status.HTTP_404_NOT_FOUND)

    essentials_list = []
    for row in rows:
        essentials_list.append({
            "ID": row[0],
            "classroom_essentials_name": row[1],
            "classroom_essentials_description": row[2],
            "ID": row[3],
            "is_activate": row[4]
        })

    return Response(essentials_list, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def show_classroom_essentials_by_id(request):
    input_data = JSONParser().parse(request)
    essentials_id = input_data.get('essentials_id')
    
    if not essentials_id:
        return Response({"error": "Essentials ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, classroom_essentials_name, classroom_essentials_description, ID, is_activate FROM eduapp.msa_classroom_essentials WHERE ID = {essentials_id}"
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return Response({"message": "Classroom essentials not found"}, status=status.HTTP_404_NOT_FOUND)

    essentials_detail = {
        "ID": row[0],
        "classroom_essentials_name": row[1],
        "classroom_essentials_description": row[2],
        "ID": row[3],
        "is_activate": row[4]
    }

    return Response(essentials_detail, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def edit_classroom_essentials(request):
    input_data = JSONParser().parse(request)
    essentials_id = input_data.get('essentials_id')
    classroom_essentials_name = input_data.get('classroom_essentials_name')
    classroom_essentials_description = input_data.get('classroom_essentials_description')
    ID = input_data.get('ID')
    is_activate = input_data.get('is_activate')

    if not essentials_id:
        return Response({"error": "Essentials ID is required to update"}, status=status.HTTP_400_BAD_REQUEST)

    updatesql = "UPDATE eduapp.msa_classroom_essentials SET"

    if classroom_essentials_name:
        updatesql += f" classroom_essentials_name = '{classroom_essentials_name}',"
    if classroom_essentials_description:
        updatesql += f" classroom_essentials_description = '{classroom_essentials_description}',"
    if ID:
        updatesql += f" ID = {ID},"
    if is_activate is not None:
        updatesql += f" is_activate = {is_activate}"

    updatesql += f" WHERE ID = {essentials_id}"

    cursor = connection.cursor()
    cursor.execute(updatesql)
    connection.commit()
    cursor.close()

    return Response({"message": "Classroom essentials updated successfully"}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def show_active_classroom_essentials(request):
    sql = "SELECT ID, classroom_essentials_name, classroom_essentials_description, ID FROM eduapp.msa_classroom_essentials WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active classroom essentials found"}, status=status.HTTP_404_NOT_FOUND)

    essentials_list = []
    for row in rows:
        essentials_list.append({
            "ID": row[0],
            "classroom_essentials_name": row[1],
            "classroom_essentials_description": row[2],
            "ID": row[3]
        })

    return Response(essentials_list, status=status.HTTP_200_OK)

# show active classroom essentials by course id
@api_view(['POST'])
def show_active_classroom_essentials_by_course_id(request):
    input_data = JSONParser().parse(request)
    ID = input_data.get('ID')
    
    if not ID:
        return Response({"error": "Course ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, classroom_essentials_name, classroom_essentials_description FROM eduapp.msa_classroom_essentials WHERE is_activate = 1 AND ID = {ID}"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active classroom essentials found for this course"}, status=status.HTTP_404_NOT_FOUND)

    essentials_list = []
    for row in rows:
        essentials_list.append({
            "ID": row[0],
            "classroom_essentials_name": row[1],
            "classroom_essentials_description": row[2]
        })

    return Response(essentials_list, status=status.HTTP_200_OK)

# CREATE TABLE `eduapp`.`msa_class_level` (
#   `ID` INT NOT NULL AUTO_INCREMENT,
#   `class_name` VARCHAR(45) NULL,
#   `is_activate` VARCHAR(45) NULL,
#   PRIMARY KEY (`ID`));

# msa_class_level
@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def add_class_level(request):
    if request.method == 'POST':
        input_data = JSONParser().parse(request)
        class_name = input_data.get('class_name')
        is_activate = input_data.get('is_activate')

        if not class_name:
            return Response({"error": "Class name is required"}, status=status.HTTP_400_BAD_REQUEST)

        sql = f"""INSERT INTO eduapp.msa_class_level (class_name, is_activate)
                  VALUES ('{class_name}', 1)"""
        cursor = connection.cursor()            
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        return Response({"message": "Class level added successfully"}, status=status.HTTP_201_CREATED)
    

@api_view(['GET'])      
@permission_classes([IsAuthenticated])
def show_all_class_levels(request):
    sql = "SELECT ID, class_name, is_activate FROM eduapp.msa_class_level"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No class levels found"}, status=status.HTTP_404_NOT_FOUND)

    class_level_list = []
    for row in rows:
        class_level_list.append({
            "ID": row[0],
            "class_name": row[1],
            "is_activate": row[2]
        })

    return Response(class_level_list, status=status.HTTP_200_OK)

# shoe all class levels by id
@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def show_class_level_by_id(request):
    input_data = JSONParser().parse(request)
    class_level_id = input_data.get('class_level_id')
    
    if not class_level_id:
        return Response({"error": "Class level ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, class_name, is_activate FROM eduapp.msa_class_level WHERE ID = {class_level_id}"
    cursor = connection.cursor()    
    cursor.execute(sql)
    row = cursor.fetchone()

    cursor.close()
    if not row:
        return Response({"message": "Class level not found"}, status=status.HTTP_404_NOT_FOUND) 
    class_level_detail = {
        "ID": row[0],
        "class_name": row[1],
        "is_activate": row[2]
    }
    return Response(class_level_detail, status=status.HTTP_200_OK)

# edit class level
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_class_level(request):
    input_data = JSONParser().parse(request)
    class_level_id = input_data.get('class_level_id')
    class_name = input_data.get('class_name')
    is_activate = input_data.get('is_activate')

    if not class_level_id:
        return Response({"error": "Class level ID is required to update"}, status=status.HTTP_400_BAD_REQUEST)

    updatesql = "UPDATE eduapp.msa_class_level SET"

    if class_name:
        updatesql += f" class_name = '{class_name}',"
    if is_activate is not None:
        updatesql += f" is_activate = {is_activate}"

    updatesql += f" WHERE ID = {class_level_id}"

    cursor = connection.cursor()
    cursor.execute(updatesql)
    connection.commit()
    cursor.close()

    return Response({"message": "Class level updated successfully"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_active_class_levels(request):
    sql = "SELECT ID, class_name FROM eduapp.msa_class_level WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active class levels found"}, status=status.HTTP_404_NOT_FOUND)

    class_level_list = []
    for row in rows:
        class_level_list.append({
            "ID": row[0],
            "class_name": row[1]
        })

    return Response(class_level_list, status=status.HTTP_200_OK)

# msa_cetagory_level
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category_level(request):
    if request.method == 'POST':
        input_data = JSONParser().parse(request)
        cetagory_name = input_data.get('cetagory_name')

        if not cetagory_name:
            return Response({"error": "Category name is required"}, status=status.HTTP_400_BAD_REQUEST)

        sql = f"""INSERT INTO eduapp.msa_cetagory_level (cetagory_name, is_activate)
                  VALUES ('{cetagory_name}', 1)"""
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()

        return Response({"message": "Category level added successfully"}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_all_category_levels(request):
    sql = "SELECT ID, cetagory_name, is_activate FROM eduapp.msa_cetagory_level"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No category levels found"}, status=status.HTTP_404_NOT_FOUND)

    category_list = []
    for row in rows:
        category_list.append({
            "ID": row[0],
            "cetagory_name": row[1],
            "is_activate": row[2]
        })

    return Response(category_list, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def show_category_level_by_id(request):
    input_data = JSONParser().parse(request)
    category_id = input_data.get('category_id')
    
    if not category_id:
        return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    sql = f"SELECT ID, cetagory_name, is_activate FROM eduapp.msa_cetagory_level WHERE ID = {category_id}"
    cursor = connection.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    cursor.close()

    if not row:
        return Response({"message": "Category level not found"}, status=status.HTTP_404_NOT_FOUND)

    category_detail = {
        "ID": row[0],
        "cetagory_name": row[1],
        "is_activate": row[2]
    }

    return Response(category_detail, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_category_level(request):
    input_data = JSONParser().parse(request)
    category_id = input_data.get('category_id')
    cetagory_name = input_data.get('cetagory_name')
    is_activate = input_data.get('is_activate')

    if not category_id:
        return Response({"error": "Category ID is required to update"}, status=status.HTTP_400_BAD_REQUEST)

    updatesql = "UPDATE eduapp.msa_cetagory_level SET"

    if cetagory_name:
        updatesql += f" cetagory_name = '{cetagory_name}',"
    if is_activate is not None:
        updatesql += f" is_activate = {is_activate}"

    updatesql += f" WHERE ID = {category_id}"

    cursor = connection.cursor()
    cursor.execute(updatesql)
    connection.commit()
    cursor.close()

    return Response({"message": "Category level updated successfully"}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_active_category_levels(request):
    sql = "SELECT ID, cetagory_name FROM eduapp.msa_cetagory_level WHERE is_activate = 1"
    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()

    if not rows:
        return Response({"message": "No active category levels found"}, status=status.HTTP_404_NOT_FOUND)

    category_list = []
    for row in rows:
        category_list.append({
            "ID": row[0],
            "cetagory_name": row[1]
        })

    return Response(category_list, status=status.HTTP_200_OK)
