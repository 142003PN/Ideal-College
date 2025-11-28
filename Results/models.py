from django.db import models
from Registration.models import Registration
from Students.models import Student
from Courses.models import Courses
from Academics.models import SessionYear
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Create your models here.
class Results(models.Model):
    result_id=models.AutoField(primary_key=True)
    registraion_id=models.ForeignKey(Registration, on_delete=models.CASCADE)
    student_id=models.ForeignKey(Student, on_delete=models.CASCADE)
    course=models.ForeignKey(Courses, on_delete=models.CASCADE)
    session_year=models.ForeignKey(SessionYear, on_delete=models.SET_NULL, null=True, blank=True)
    mark=models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    grade=models.CharField(max_length=5, null=True, blank=True)
    date_recorded=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs ):
        mark=int(self.mark)
        if mark >= 80:
            self.grade = 'A'
        elif mark >= 70:
            self.grade = 'B'
        elif mark >= 60:
            self.grade = 'C'
        elif mark==0:
            self.grade = None
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return super().__str__()

@receiver(m2m_changed, sender=Registration.courses.through)
def create_results_for_new_courses(sender, instance, action, **kwargs):
    if action == 'post_add':
        student = instance.student_id
        session_year = instance.session_year
        for course in instance.courses.all():
            Results.objects.get_or_create(
                registraion_id=instance,
                student_id=student,
                course=course,
                session_year=session_year
            )