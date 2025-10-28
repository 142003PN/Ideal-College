from django.db import models
import uuid
from Programs.models import Programs

# Create your models here.
class YearOfStudy(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    year_title = models.CharField(max_length=50)
    #is_current_year = models.BooleanField(default=False)

    def __str__(self):
        return self.year_title
class Courses(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    course_code = models.CharField(max_length=20, unique=True)
    course_title = models.CharField(max_length=100)
    program_id = models.ForeignKey(Programs, null=True, blank=True, on_delete=models.CASCADE)
    year_of_study = models.ForeignKey(YearOfStudy, blank=True, null=True, on_delete=models.CASCADE)
    date_adde = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_code +'--'+ self.course_title
    