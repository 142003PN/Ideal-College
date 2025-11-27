from django.db import models
import uuid
from Departments.models import Department
from Staff.models import *
# Create your models here.
class Programs(models.Model):
    id = models.AutoField(primary_key=True)
    program_title = models.CharField(max_length=100, unique=True)
    department_id = models.ForeignKey(Department, related_name='department', on_delete=models.SET_NULL, null=True, blank=True)
    added_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.program_title
    