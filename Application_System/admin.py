from django.contrib import admin
from .models import General_Information, School_Certificate, Application_Status, Next_of_Kin
# Register your models here.
@admin.register(General_Information)
class GeneralInformationAdmin(admin.ModelAdmin):
    list_display = ('admission_id', 'first_name', 'last_name', 'date_of_birth', 'NRC', 'email', 'date_of_application')
    search_fields = ('admission_id', 'first_name', 'last_name', 'NRC', 'email')

@admin.register(School_Certificate)
class SchoolCertificateAdmin(admin.ModelAdmin):
    list_display = ('addmission', 'certificate_type', 'institution_name', 'year_of_completion')
    search_fields = ('addmission__admission_id', 'institution_name', 'certificate_name')

@admin.register(Application_Status)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('application', 'status')
    search_fields = ('application__admission_id', 'status')

admin.site.register(Next_of_Kin)