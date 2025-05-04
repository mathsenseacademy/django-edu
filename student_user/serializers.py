from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        # fields = ['id', 'name', 'email', 'date_of_birth', 'registered_at']
        # exclude = ['registered_at']  # Example of excluding a field