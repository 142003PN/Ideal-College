from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import datetime
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, NRC, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, NRC=NRC, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, NRC, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if not password:
            raise ValueError('The Password field must be set for superuser.')

        return self.create_user(email, first_name, last_name, NRC, password, **extra_fields)
    
class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        STUDENT = 'STUDENT', 'Student'
    username = None
    email = models.EmailField(unique=True)  
    NRC = models.CharField(max_length=20, unique=True, null=True, blank=True) 
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.STUDENT) 
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['first_name','last_name', 'NRC', 'email']

    def __str__(self):
        return self.first_name+" "+self.last_name+" "+self.email