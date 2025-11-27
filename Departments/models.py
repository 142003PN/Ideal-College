from django.db import models
from django.utils import timezone
import uuid
from Users.models import CustomUser
# Create your models here.
class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=100)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by=models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.department_name