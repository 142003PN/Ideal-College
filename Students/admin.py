from django.contrib import admin
from .models import Student, StudentProfile

# Register your models here.
admin.site.register(StudentProfile)
admin.site.register(Student)