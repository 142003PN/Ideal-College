from django.db import models

# Create your models here.
class SessionYear(models.Model):
    year_title=models.CharField(max_length=20, null=True)
    is_current_year=models.BooleanField(default=False)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.year_title