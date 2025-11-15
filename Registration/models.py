from django.db import models
from Students.models import Student
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
# Create your models here.
class Registration(models.Model):
    class STATUS(models.TextChoices):
        Pending = 'Pending', 'Pending'
        Approved = 'Approved', 'Approved'
    student_id=models.ForeignKey(Student, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    courses=models.ManyToManyField(Courses, related_name='registrations')
    status=models.CharField(max_length=10, choices=STATUS.choices, default='Pending')
    year_of_study=models.ForeignKey(YearOfStudy, on_delete=models.SET_NULL, blank=True, null=True)
    session_year=models.ForeignKey(SessionYear,on_delete=models.CASCADE)
    registraion_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.courses} - {self.session_year}"