from django.db import models
from django.core.validators import FileExtensionValidator
import datetime
from django.core import validators
from Students.models import Student, StudentProfile
from Academics.models import YearOfStudy, Intake, SessionYear
from Programs.models import Programs
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from Users.models import CustomUser
from django.contrib.auth.hashers import make_password

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
    NRC_scan = models.FileField(upload_to='nrc_scans/', null=True, blank=True)
    marital_status = models.CharField(max_length=30, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    nationality = models.CharField(max_length=50)
    intake = models.ForeignKey(Intake, on_delete=models.SET_NULL, null=True, blank=True)
    #contact details
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True)
    city_of_residence = models.CharField(max_length=50, null=True, blank=True)
    #disability
    disability = models.CharField(max_length=5, default="No")
    disability_desc=models.CharField(max_length=15, null=True, blank=True)
    #year_of_study = models.ForeignKey(YearOfStudy, on_delete=models.SET_NULL, null=True, blank=True)#should added by default to first year
    program = models.ForeignKey(Programs, null=True, blank=True, on_delete=models.SET_NULL, related_name='applications')
    deposit_slip = models.FileField(upload_to='slips/', null=True, blank=True)
    date_of_application = models.DateField(auto_now_add=True)
    passport_photo = models.ImageField(upload_to='profile_picture', default='fallback.png', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
#---------------Next of Kin-----------------                    
class Next_of_Kin(models.Model):
    addmission_id = models.OneToOneField(General_Information, on_delete=models.CASCADE, related_name='next_of_kin')
    full_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=15, null=False)
    NK_address = models.TextField(null=True)
    def __str__(self):
        return self.full_name
    
#--------Subject Results--------------------
class CertificateResults(models.Model):
    admission_id = models.ForeignKey(General_Information, on_delete=models.CASCADE, related_name='results')
    subject_name = models.CharField(max_length=30)
    grade=models.PositiveIntegerField()

    def __str__(self):
        return self.subject_name
    
#---------------School Certificate-----------------
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
    
#---------------Application Status-----------------
class Application_Status(models.Model):
    application = models.OneToOneField(General_Information, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ], default='PENDING')
    accepted_by=models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.status
#signal to create Application_Status upon General_Information creation
@receiver(post_save, sender=General_Information)
def create_application_status(sender, instance, created, **kwargs):
    if created:
        Application_Status.objects.create(application=instance)

from datetime import datetime
from django.db.models import Max

@receiver(post_save, sender=Application_Status)
def create_student_on_approval(sender, instance, created, **kwargs):
    if instance.status != 'APPROVED':
        return

    app = instance.application

    try:
        # ===== GENERATE STUDENT ID =====
        intake_obj = app.intake
        intake = intake_obj.intake_name if intake_obj else 'unknown'

        year = datetime.now().year

        if intake.lower() == 'january':
            intake_code = '01'
        elif intake.lower() == 'july':
            intake_code = '02'
        else:
            intake_code = '00'

        prefix = f"{year}{intake_code}01"

        last_student = Student.objects.filter(id__startswith=prefix).order_by('-id').first()

        if last_student:
            last_serial = int(str(last_student.id)[-2:])
            new_serial = last_serial + 1
        else:
            new_serial = 1

        serial = str(new_serial).zfill(2)
        student_id = f"{prefix}{serial}"

        # ===== CREATE STUDENT =====
        student, _ = Student.objects.update_or_create(
            email=app.email,
            defaults={
                'id': student_id,
                'first_name': app.first_name,
                'last_name': app.last_name,
                'NRC': app.NRC,
                'password': (
                    'pbkdf2_sha256$1000000$9OIhdL3lzqkLj3EflnZvAX$'
                    'aAmj8j+gYKa+z9iI3b/ogjL5RRWTJIVUZzvweQeINQ8='
                ),
            }
        )

        # ===== CREATE / UPDATE PROFILE =====
        StudentProfile.objects.update_or_create(
            student_id=student,
            defaults={
                'date_of_birth': app.date_of_birth,
                'address': app.address,
                'phone_number': app.phone_number,
                'program': app.program,
                'gender': app.gender,
                'profile_picture': app.passport_photo,
            }
        )

    except Exception as e:
        logger.exception("PROFILE ERROR: %s", str(e))
        raise e  # <-- REMOVE SILENT FAILING
