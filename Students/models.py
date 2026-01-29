from django.db import models
from Users.models import CustomUser, CustomUserManager
from Programs.models import Programs
from Academics.models import YearOfStudy, Intake
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File

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
    profile_picture = models.ImageField(upload_to='student_profiles/', default='fallback.png', blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, null=True, blank=True)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.make(f"https://http://sis-ichas.com/results/print/{self.student_id}/")
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            filename = f'student_{self.id}_qr.png'
            self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.student_id.first_name}'s Profile"
    
    