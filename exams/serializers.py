from rest_framework import serializers
from .models import QuestionTable, ExamTable

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionTable
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamTable
        fields = '__all__'
