from rest_framework import serializers
from .models import Administrator

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
