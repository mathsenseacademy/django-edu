from rest_framework_simplejwt.authentication import JWTAuthentication
from administrator.models import Administrator
from rest_framework.exceptions import AuthenticationFailed

class AdminJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        admin_id = validated_token.get("admin_id")
        if not admin_id:
            raise AuthenticationFailed("admin_id not in token")
        try:
            return Administrator.objects.get(id=admin_id)
        except Administrator.DoesNotExist:
            raise AuthenticationFailed("Administrator not found")
