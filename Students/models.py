from django.db import models
from Users.models import CustomUser, CustomUserManager
from Programs.models import Programs
from Academics.models import YearOfStudy
from django.db.models.signals import post_save
from django.dispatch import receiver

class StudentManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=CustomUser.Roles.STUDENT)
    
class Student(CustomUser):
    base_role = CustomUser.Roles.STUDENT
    class Meta:
        proxy = True
        app_label = 'Students'
    def save(self, *args, **kwargs):
        self.role = self.base_role
        return super().save(*args, **kwargs)
    @classmethod
    def get_queryset(cls):
        return cls.objects.filter(role=cls.base_role)

class StudentProfile(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
    student_id = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='profile')
    program = models.ForeignKey(Programs, on_delete=models.SET_NULL, null=True, blank=True)
    year_of_study = models.ForeignKey(YearOfStudy, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', default='fallback.png', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.student_id.first_name}'s Profile"
    
    