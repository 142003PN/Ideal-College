"""from django.db import models
from django.core.validators import FileExtensionValidator
import datetime
from django.core import validators
from Students.models import Student, StudentProfile
from Programs.models import Programs
# Create your models here.
class General_Information(models.Model):
    admission_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(validators=[
        validators.MinValueValidator(
            limit_value=datetime.date.today() - datetime.timedelta(days=365.25*100),
            message='Date of birth cannot be more than 100 years ago'
        ),
        validators.MaxValueValidator(
            limit_value=datetime.date.today() - datetime.timedelta(days=365.25*16),
            message='Must be at least 16 years old'
        )
    ])
    nationality = models.CharField(max_length=50)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    NRC = models.CharField(max_length=20, unique=True)
    scan_of_slip = models.FileField(upload_to='slips/', validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])])
    date_of_application = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.admission_id}"
    
class School_Certificate(models.Model):
    class TypeChoices(models.TextChoices):
        SECONDARY = 'SECONDARY', 'Secondary_School_Certificate'
        DIPLOMA = 'DIPLOMA', 'Diploma'
        DEGREE = 'DEGREE', 'Degree'
        ADVANCED_cERTIFICATE = 'ADVANCED_CERTIFICATE', 'Advanced_Certificate'
        OTHER = 'OTHER', 'Other'
    addmission = models.ForeignKey(General_Information, on_delete=models.CASCADE)
    certificate_type = models.CharField(max_length=30, choices=TypeChoices.choices)
    certificate_name = models.CharField(max_length=100, null=True, blank=True)
    institution_name = models.CharField(max_length=100, null=True, blank=True)
    scan_copy = models.FileField(upload_to='certificates/', validators=[FileExtensionValidator(['pdf'])])

    def __str__(self):
        return f"{self.certificate_name} - {self.institution_name}"

class Application_Status(models.Model):
    application = models.OneToOneField(General_Information, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')
    reviewed_by = models.ForeignKey('Staff.Staff', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Application {self.application.admission_id} - {self.status}"
    

"""