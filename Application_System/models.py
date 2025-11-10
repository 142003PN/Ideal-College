from django.db import models
from django.core.validators import FileExtensionValidator
import datetime
from django.core import validators
from Students.models import Student, StudentProfile
from Courses.models import YearOfStudy
from Programs.models import Programs
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)
# Create your models here.
class General_Information(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
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
    NRC = models.CharField(max_length=20, unique=True)
    marital_status = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    nationality = models.CharField(max_length=50)
    #contact details
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    city_of_residence = models.CharField(max_length=50, null=True, blank=True)
    #disability
    disability = models.CharField(max_length=5, default="No")
    disability_desc=models.CharField(max_length=15, null=True, blank=True)
    year_of_study = models.ForeignKey(YearOfStudy, on_delete=models.SET_NULL, null=True, blank=True)#should added by default to first year
    program = models.ForeignKey(Programs, null=True, blank=True, on_delete=models.SET_NULL)
    deposit_slip = models.FileField(upload_to='slips/', validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])])
    date_of_application = models.DateField(auto_now_add=True)
    passport_photo = models.ImageField(upload_to='profile_picture', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
#next of Kin
class Next_of_Kin(models.Model):
    addmission_id = models.OneToOneField(General_Information, on_delete=models.CASCADE, related_name='next_of_kin')
    full_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    phone_number = models.CharField(max_length=15, null=False)
    NK_address = models.TextField(null=True)
    def __str__(self):
        return self.full_name
#Subjects
class CertificateResults(models.Model):
    admission_id = models.ForeignKey(General_Information, on_delete=models.CASCADE, related_name='results')
    subject_name = models.CharField(max_length=10)
    grade=models.PositiveIntegerField()

    def __str__(self):
        return self.subject_name
    
#school certificate
class School_Certificate(models.Model):
    class TypeChoices(models.TextChoices):
        ECONDARY = 'SECONDARY', 'Secondary_School_Certificate'
        DIPLOMA = 'DIPLOMA', 'Diploma'
        DEGREE = 'DEGREE', 'Degree'
        ADVANCED_cERTIFICATE = 'ADVANCED_CERTIFICATE', 'Advanced_Certificate'
        OTHER = 'OTHER', 'Other'
    addmission = models.ForeignKey(General_Information, on_delete=models.CASCADE, related_name='certficate')
    certificate_type = models.CharField(max_length=30, choices=TypeChoices.choices)
    certificate_name = models.CharField(max_length=100, null=True, blank=True)
    institution_name = models.CharField(max_length=100, null=True, blank=True)
    certificate = models.FileField(upload_to='certificates/', validators=[FileExtensionValidator(['pdf'])])
    year_of_completion = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.certificate_type} - {self.institution_name} ({self.year_of_completion})"
#application status
class Application_Status(models.Model):
    application = models.OneToOneField(General_Information, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')
    def __str__(self):
        return self.status
    
# Signal to create Student and StudentProfile upon application approval  
@receiver(post_save, sender=Application_Status)
def create_student_on_approval(sender, instance, created, **kwargs):
    # Only act when application status is approved
    if instance.status != 'APPROVED':
        return
    app = instance.application
    try:
        # Create or get Student using the unique email from General_Information.
        student, student_created = Student.objects.get_or_create(
            email=app.email,
            defaults={
                'first_name': app.first_name,
                'last_name': app.last_name,
                'NRC': app.NRC,
            }
        )
        # Create or get StudentProfile linked to the created/found Student.
        profile, profile_created = StudentProfile.objects.get_or_create(
            student_id=student,
            defaults={
                'date_of_birth': app.date_of_birth,
                'address': app.address,
                'phone_number': app.phone_number,
                'program': app.program,
                'year_of_study': app.year_of_study,
                'gender': app.gender
            }
        )
    except Exception:
        logger.exception("Error creating Student or StudentProfile for application id %s", app.admission_id)

