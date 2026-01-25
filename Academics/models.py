from django.db import models
from Users.models import CustomUser
import uuid
# Create your models here.

#year of study
class YearOfStudy(models.Model):
    class YearChoices(models.TextChoices):
        First_Year = 'First Year'
        Second_Year = 'Second Year'
        Third_Year = 'Third Year'
        Fourth_Year = 'Fourth Year'
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    year_title = models.CharField(max_length=50, choices=YearChoices.choices, null=True, unique=True)

    def __str__(self):
        return self.year_title

#Intakes
class Intake(models.Model):
    class IntakeChoices(models.TextChoices):
        January = 'January'
        May = 'July'
    intake_name=models.CharField(max_length=20, choices=IntakeChoices.choices, null=True, unique=True)
    date=models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.intake_name
    
#-----------Semesters---------------
class Semester(models.Model):
    class SemesterChoices(models.TextChoices):
        Semester_1 = 'semester_1'
        Semester_2 = 'semester_2'
    semester_name=models.CharField(max_length=20, choices=SemesterChoices.choices, null=True, unique=True)
    date=models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    def __str__(self):  
        return self.semester_name

#----------------SessionYear--------------------
class SessionYear(models.Model):
    year_title=models.CharField(max_length=20, null=True)
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, null=True, related_name='intakes')
    is_current_year=models.BooleanField(default=False)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name='semester')
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.year_title