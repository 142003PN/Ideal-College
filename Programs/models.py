from django.db import models
import uuid
from Departments.models import Department
# Create your models here.
class Programs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program_title = models.CharField(max_length=100)
    department_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    #added_by = models.BigIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.program_title
    