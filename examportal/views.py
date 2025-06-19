from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser

from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


'''this function is used to create a new question in the database.
It takes the question text, option count, and marks as input.'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createquestion(request):
    input_data =  JSONParser().parse(request)
    question = input_data.get('question')
    optioncount = input_data.get('optioncount')
    marks = input_data.get('marks')

    sql = f"""INSERT INTO examportal_questions (question, optioncount, marks, is_active) 
                VALUES ('{question}', {optioncount}, {marks}, 1)"""
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return Response({"message": "Question created successfully"}, status=status.HTTP_201_CREATED)

'''this function is used to edit an existing question in the database.
It takes the question text, option count, marks, and is_active status as input.'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def editquestion(request):
    input_data =  JSONParser().parse(request)
    question = input_data.get('question')
    optioncount = input_data.get('optioncount')
    marks = input_data.get('marks')
    isActive = input_data.get('isactive')
    updatesql = ""

    if question:
        updatesql += f" SET question = '{question}'"
    if optioncount:
        updatesql += f"optioncount = {optioncount}" 
    if marks:   
        updatesql += f"marks = {marks}"
    if isActive:        
        updatesql += f"is_active = {isActive}"
    updatesql += f" WHERE ID = {input_data.get('id')}"
    cursor = connection.cursor()
    cursor.execute(updatesql)

    connection.commit()
    cursor.close()
    return Response({"message": "Question updated successfully"}, status=status.HTTP_200_OK)

'''this function is used to delete a question from the database.
It takes the question ID as input. 
This one to display all active questions.'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getquestions(request):
    input_data =  JSONParser().parse(request)
    sql = f"""SELECT question, optioncount, marks FROM examportal_questions 
    WHERE ID = {input_data.get('id')} AND is_active = 1 """
    cursor = connection.cursor()
    cursor.execute(sql)
    questions = cursor.fetchall()
    connection.commit()
    cursor.close()
    return Response({"questions": questions}, status=status.HTTP_200_OK)

'''this function is used to retrieve all questions from the database.
 Mainly use for displaying all questions.'''    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getallquestions(request):
    sql = "SELECT question, optioncount, marks, is_active FROM examportal_questions"
    cursor = connection.cursor()
    cursor.execute(sql)
    questions = cursor.fetchall()
    connection.commit()
    cursor.close()
    return Response({"questions": questions}, status=status.HTTP_200_OK)

'''this function is used to retrieve a question by its ID from the database. 
Mainly use for editing.'''
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def getquestionbyid(request):
    input_data =  JSONParser().parse(request)
    question_id = input_data.get('id')
    sql = f"SELECT question, optioncount, marks, is_active FROM examportal_questions WHERE ID = {question_id}"
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        question = cursor.fetchone()
        connection.commit()
        cursor.close()
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()  
    
    return Response({"question": question}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_answer(request):
    input_data =  JSONParser().parse(request)
    question_id = input_data.get('questionid')
    answer = input_data.get('answer')
    is_correct = input_data.get('is_correct', 0)  # Default to 0 if not provided
    # Check if the question ID exists
    sql = f"SELECT * FROM eduapp.examportal_questions WHERE ID = {question_id} AND is_active = 1"
    print(f"first sql: {sql}")  
    try:
        cursor = connection.cursor()
        cursor.execute(sql) 
        question = cursor.fetchone()
    except Exception as e:  
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
    # Check if the question is found and is active
    if not question:
        return Response({"error": "Question not found or inactive"}, status=status.HTTP_404_NOT_FOUND)
    # check count of answers on the question is less than or equal to option count
    sql_count_of_answer = f"SELECT COUNT(*) FROM eduapp.examportal_answer WHERE questionID = {question_id} AND is_active = 1"  
    print(f"second sql: {sql_count_of_answer}") 
    try:
        cursor = connection.cursor()
        cursor.execute(sql_count_of_answer)
        answer_count = cursor.fetchone()[0]
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
    # Check if the answer count exceeds the option count
    print(f"question[1] :: {question[1]}")
    if answer_count >= question[2]:
        return Response({"error": "Answer limit reached for this question"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Insert the answer into the database
    # Check if the answer already exists for the question
    sql_exist_anser_check = f"SELECT * FROM eduapp.examportal_answer WHERE questionID = {question_id} AND answer = '{answer}'"
    print(f"third sql: {sql_exist_anser_check}")
    try:
        cursor = connection.cursor()
        cursor.execute(sql_exist_anser_check)
        existing_answer = cursor.fetchone()
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
    # Response if the answer already exists for the question
    if existing_answer:
        return Response({"error": "Answer already exists for this question"}, status=status.HTTP_400_BAD_REQUEST)
    # Insert the new answer
    insert_answer_sql = f"""INSERT INTO eduapp.examportal_answer (questionID, answer, is_correct, is_active) 
                VALUES ({question_id}, '{answer}', {is_correct},1)"""
    print(f"fourth sql: {insert_answer_sql}")
    try:
   
        cursor = connection.cursor()
        cursor.execute(insert_answer_sql)
        connection.commit()
        cursor.close()
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:    
        cursor.close()
    
    return Response({"message": "Answer added successfully"}, status=status.HTTP_201_CREATED)

# This function is used to edit an existing answer in the database.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_answer(request):
    input_data =  JSONParser().parse(request)
    question_id = input_data.get('questionid')
    answer = input_data.get('answer')
    is_correct = input_data.get('is_correct', 0)  # Default to 0 if not provided
    is_active = input_data.get('is_active', 1)  # Default to 1 if not provided

    #  update the answer in the database
    sql = f"""UPDATE examportal_answers 
                SET answer = '{answer}', is_correct = {is_correct}, is_active = {is_active} 
                WHERE questionid = {question_id}"""
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
    return Response({"message": "Answer updated successfully"}, status=status.HTTP_200_OK)

# Activate inactivate answer
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activate_inactivate_answer(request):
    input_data =  JSONParser().parse(request)
    answer_id = input_data.get('id')
    is_active = input_data.get('is_active', 1)  # Default to 1 if not provided
    #  update the answer in the database
    sql = f"""UPDATE examportal_answers 
                SET is_active = {is_active} 
                WHERE ID = {answer_id}"""
    try:    
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
    except Exception as e:
        connection.rollback()
        cursor.close()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()

    return Response({"message": "Answer updated successfully"}, status=status.HTTP_200_OK)