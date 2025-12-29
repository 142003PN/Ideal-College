from django.db import models
from Students.models import Student
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
from django.db.models.signals import post_save, pre_save, m2m_changed
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.conf import settings
from django.urls import reverse

from django.dispatch import receiver
from Students.models import StudentProfile
# Create your models here.
class Registration(models.Model):
    class STATUS(models.TextChoices):
        Pending = 'Pending', 'Pending'
        Approved = 'Approved', 'Approved'
    student_id=models.ForeignKey(Student, on_delete=models.CASCADE, related_name="registration", limit_choices_to={'role': 'STUDENT'})
    courses=models.ManyToManyField(Courses, related_name='registrations')
    status=models.CharField(max_length=10, choices=STATUS.choices, default='Pending')
    year_of_study=models.ForeignKey(YearOfStudy, on_delete=models.SET_NULL, blank=True, null=True)
    session_year=models.ForeignKey(SessionYear,on_delete=models.CASCADE, related_name='session_years')
    registration_date=models.DateTimeField(auto_now_add=True)
    qr_code=models.ImageField(upload_to='registration_qr_codes', blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.courses} - {self.session_year}"
    
    def save(self, *args, **kwargs):
        # Generate QR code if status is Approved and QR code doesn't exist
        if self.status == 'Approved' and not self.qr_code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            url = f"{settings.SITE_URL}{reverse('Registration:print_slip', args=[self.student_id.id])}"
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to ImageField
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            self.qr_code.save(f'registration_{self.id}.png', File(buffer), save=False)

        super().save(*args, **kwargs)

@receiver(post_save, sender=Registration)
def update_student_profile_on_approval(sender, instance, created, update_fields, **kwargs):
    # Only run when status is updated OR on creation
    if (update_fields and 'status' in update_fields) or created:
        if instance.status == 'Approved':
            # Update directly without fetching
            StudentProfile.objects.filter(student_id=instance.student_id).update(
                year_of_study=instance.year_of_study
            )

@receiver(pre_save, sender=Registration)
def delete_qr_code_on_registration_delete(sender, instance, **kwargs):
    if instance.pk:  # Check if the instance already exists
        try:
            old_instance = Registration.objects.get(pk=instance.pk)
            if old_instance.qr_code and old_instance.qr_code.name:
                old_instance.qr_code.delete(save=False)  # Delete the QR code file
        except Registration.DoesNotExist:
            pass