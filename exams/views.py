from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import QuestionTable, ExamTable
from .serializers import QuestionSerializer, ExamSerializer

# Question CRUD
@api_view(['GET', 'POST'])
def question_list(request):
    if request.method == 'GET':
        questions = QuestionTable.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def question_detail(request, pk):
    try:
        question = QuestionTable.objects.get(pk=pk)
    except QuestionTable.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = QuestionSerializer(question)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Exam CRUD
@api_view(['GET', 'POST'])
def exam_list(request):
    if request.method == 'GET':
        exams = ExamTable.objects.all()
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ExamSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def exam_detail(request, pk):
    try:
        exam = ExamTable.objects.get(pk=pk)
    except ExamTable.DoesNotExist:
        return Response({'error': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExamSerializer(exam)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ExamSerializer(exam, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        exam.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


@api_view(['POST'])
def add_questions_to_exam(request, exam_id):
    """
    Add new questions to an existing exam.
    URL example: POST /api/exams/<exam_id>/add-questions/
    Body example:
    {
        "question_ids": [3, 4]
    }
    """
    # 1. Find the exam
    try:
        exam = ExamTable.objects.get(pk=exam_id)
    except ExamTable.DoesNotExist:
        return Response(
            {'message': 'Exam not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2. Get IDs from request body
    question_ids = request.data.get('question_ids', [])
    if not question_ids:
        return Response(
            {
                'message': 'question_ids is required',
                'example': {'question_ids': [1, 2, 3]}
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Validate all given question IDs exist
    existing_questions = QuestionTable.objects.filter(questionID__in=question_ids)
    existing_ids = [q.questionID for q in existing_questions]

    invalid_ids = [qid for qid in question_ids if qid not in existing_ids]
    if invalid_ids:
        return Response(
            {
                'message': 'Invalid question IDs',
                'invalid_ids': invalid_ids
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. Merge with current questions (avoid duplicates)
    current_questions = set(exam.questionarray or [])
    new_questions = set(question_ids)
    updated_questions = list(current_questions.union(new_questions))

    # 5. Update exam fields
    exam.questionarray = updated_questions
    exam.total_no_questions = len(updated_questions)
    exam.save()

    # 6. Serialize and return
    serializer = ExamSerializer(exam)
    return Response(
        {
            'message': f'Added {len(new_questions - current_questions)} new questions',
            'exam': serializer.data
        }
    )

@api_view(['GET'])
def exam_questions(request, exam_id):
    try:
        exam = ExamTable.objects.get(pk=exam_id)
    except ExamTable.DoesNotExist:
        return Response({'message': 'Exam not found'}, status=status.HTTP_404_NOT_FOUND)

    if not exam.questionarray:
        return Response({'message': 'No questions found for this exam'}, status=status.HTTP_404_NOT_FOUND)

    questions = QuestionTable.objects.filter(questionID__in=exam.questionarray)
    serializer = QuestionSerializer(questions, many=True)
    
    return Response({
        'exam_id': exam.exam_id,
        'exam_name': exam.examName,
        'exam_duration': exam.examduration,
        'total_questions': exam.total_no_questions,
        'pass_marks': exam.passmarks,
        'questions': serializer.data
    })
