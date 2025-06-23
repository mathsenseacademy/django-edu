# from rest_framework import serializers
# from .models import Student

# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'
#         read_only_fields = ['student_id', 'is_verified', 'registered_at']

#         # fields = ['id', 'name', 'email', 'date_of_birth', 'registered_at']
#         # exclude = ['registered_at']  # Example of excluding a field


# serializers.py
from rest_framework import serializers
from .models import StudentCredential

class StudentCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCredential
        fields = ['id', 'student_id', 'student_username', 'student_password', 'is_active']
        extra_kwargs = {
            'student_password': {'write_only': True}
        }
