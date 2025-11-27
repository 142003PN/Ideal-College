from django.db import models
import uuid
import json
from Programs.models import Programs
from Staff.models import *

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
    program_id = models.ForeignKey(Programs, related_name='programs', null=True, blank=True, on_delete=models.CASCADE)
    year_of_study = models.ForeignKey(YearOfStudy, blank=True, null=True, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by=models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.course_code +'--'+ self.course_title
    def to_dict(self):
        return {"year": self.year}
