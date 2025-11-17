from django.db import models
from Users.models import CustomUser, CustomUserManager
from Departments.models import Department
# Create your models here.
class StudentManager(CustomUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=CustomUser.Roles.STUDENT)
    
class Staff(CustomUser):
    base_role = CustomUser.Roles.STAFF
    class Meta:
        proxy = True
        app_label = 'Staff'
    def save(self, *args, **kwargs):
        self.role = self.base_role
        return super().save(*args, **kwargs)
    @classmethod
    def get_queryset(cls):
        return cls.objects.filter(role=cls.base_role)
    
class StaffProfile(models.Model):
    class Positions(models.TextChoices):
        LECTURE = 'Lecturer', 'Lecturer'
        PSYCHOLOGIST = 'Psychologist', 'Pyschologist'
        LIBRARIAN = 'Librarian', 'Librarian'
        INSTRUCTOR = 'Clinical Instructor', 'Clinical Instructor'
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
    class Emp_Status(models.TextChoices):
        FullTime= 'FullTime', 'FullTime'
        PartTime = 'PartTime', 'PartTime'
    staff_id = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='staff_profile')
    position = models.CharField(max_length=30, choices=Positions.choices, null=True)
    profile_picture = models.ImageField(upload_to='staff_profiles/', default='fallback.png', blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=Emp_Status.choices)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.staff_id
    
