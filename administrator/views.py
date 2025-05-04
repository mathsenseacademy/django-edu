from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Administrator
from .serializers import AdministratorSerializer
from student_user.models import Student
from student_user.serializers import StudentSerializer

from rest_framework_simplejwt.tokens import RefreshToken


# ✅ Create token manually for custom user model
def get_tokens_for_admin(admin):
    refresh = RefreshToken()
    refresh['admin_id'] = admin.id
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# ✅ Admin Registration
@api_view(['POST'])
def admin_register(request):
    serializer = AdministratorSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()
        tokens = get_tokens_for_admin(admin)
        return Response({
            'admin_id': admin.id,
            **tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ Admin Login
@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        admin = Administrator.objects.get(username=username)
        if admin.check_password(password):
            tokens = get_tokens_for_admin(admin)
            return Response({
                'admin_id': admin.id,
                **tokens
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    except Administrator.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)


# ✅ Protected route: Admin can view all students
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_student_list(request):
    students = Student.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)
