from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from .serializers import StudentSerializer

# Student Registration
@api_view(['POST'])
def student_register(request):
    serializer = StudentSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        return Response({'id': student.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
