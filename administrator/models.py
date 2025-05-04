from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class AdministratorManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Administrators must have an email address')
        admin = self.model(username=username, email=self.normalize_email(email))
        admin.set_password(password)
        admin.save(using=self._db)
        return admin

#     def create_superuser(self, username, email, password):
#         admin = self.create_user(username, email, password)
#         admin.is_superuser = True
#         admin.is_staff = True
#         admin.save(using=self._db)
#         return admin

# class Administrator(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(max_length=255, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     objects = AdministratorManager()

#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['email']  # ✅ This is required

#     def __str__(self):
#         return self.username


class Administrator(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # ✅ Add this

    objects = AdministratorManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
