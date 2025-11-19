from django.db import models
from Students.models import Student
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
from django.db.models.signals import post_save, pre_save, m2m_changed

from django.dispatch import receiver
from Students.models import StudentProfile
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
    registration_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.courses} - {self.session_year}"

@receiver(post_save, sender=Registration)
def update_student_profile_on_approval(sender, instance, created, update_fields, **kwargs):
    # Only run when status is updated OR on creation
    if (update_fields and 'status' in update_fields) or created:
        if instance.status == 'Approved':
            # Update directly without fetching
            StudentProfile.objects.filter(student_id=instance.student_id).update(
                year_of_study=instance.year_of_study
            )
