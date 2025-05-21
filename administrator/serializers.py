from rest_framework import serializers
from .models import Administrator, CourseType, Course

class AdministratorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Administrator
        fields = ['username', 'email', 'password', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        admin = Administrator(**validated_data)
        admin.set_password(raw_password)
        admin.save()
        return admin
    
class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseType
        fields = ['id', 'name', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'type', 'student_class', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
