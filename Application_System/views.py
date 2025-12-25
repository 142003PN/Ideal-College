from django.shortcuts import render, redirect
from Programs.models import Programs
from Students.models import *
from .models import *
from Courses.models import YearOfStudy
from django.contrib import messages
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import *
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
import threading
from django.db import transaction
import tempfile
from django.core.files.storage import FileSystemStorage

class EmailThread(threading.Thread):
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send(fail_silently=False)

def step1_general_info(request):
    programs = Programs.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        NRC = request.POST.get('NRC')

        if Student.objects.filter(email=email).exists() or General_Information.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        elif Student.objects.filter(NRC=NRC).exists() or General_Information.objects.filter(NRC=NRC).exists():
            messages.error(request, 'NRC already exists!')
        elif len(NRC) > 15:
            messages.error(request, "NRC should have less than 15 characters")
        elif not all(c.isdigit() or c == '/' for c in NRC):
            messages.error(request, "NRC should only contain numbers and forward slashes /")
        else:
            # Save files temporarily
            fs = FileSystemStorage(location=tempfile.gettempdir())
            nrc_scan = request.FILES.get('NRC_scan')
            deposit_slip = request.FILES.get('deposit_slip')
            passport_photo = request.FILES.get('passport_photo')

            #valisation
            program_id = request.POST.get('program')
            request.session['general_info'] = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'date_of_birth': request.POST.get('date_of_birth'),
                'NRC': request.POST.get('NRC'),
                'marital_status': request.POST.get('marital_status'),
                'gender': request.POST.get('gender'),
                'nationality': request.POST.get('nationality'),
                'address': request.POST.get('address'),
                'phone_number': request.POST.get('phone_number'),
                'email': request.POST.get('email'),
                'city_of_residence': request.POST.get('city_of_residence'),
                'disability': request.POST.get('disability'),
                'disability_desc': request.POST.get('disability_desc'),
                'program_id': program_id,

                # file paths
                'NRC_scan': fs.save(nrc_scan.name, nrc_scan) if nrc_scan else None,
                'deposit_slip': fs.save(deposit_slip.name, deposit_slip),
                'passport_photo': fs.save(passport_photo.name, passport_photo),
            }

            return redirect('Application:step2')

        # LOAD EXISTING SESSION DATA
    context = {
        'progress': 25,
        'data': request.session.get('general_info', {}),
        'programs':programs,
    }

    return render(request, 'applications/step1_general_info.html', context)


def step2_next_of_kin(request):
    if request.method == 'POST':
        request.session['next_of_kin'] = {
            'full_name': request.POST.get('full_name'),
            'email': request.POST.get('email'),
            'phone_number': request.POST.get('phone_number'),
            'NK_address': request.POST.get('NK_address'),
        }
        return redirect('Application:step3')

    context = {'progress': 50,
    'data': request.session.get('next_of_kin', {})
    }

    return render(request, 'applications/step2_next_of_kin.html', context)

def step3_results(request):
    if request.method == 'POST':
        subjects = request.POST.getlist('subject_name')
        grades = request.POST.getlist('grade')

        request.session['results'] = [
            {'subject_name': s, 'grade': g}
            for s, g in zip(subjects, grades)
        ]

        return redirect('Application:step4')

    return render(request, 'applications/step3_results.html', {
        'progress': 75,
        'results': request.session.get('results', [])
    })


def step4_certificate(request):
    if request.method == 'POST':
        fs = FileSystemStorage(location=tempfile.gettempdir())

        types = request.POST.getlist('certificate_type[]')
        names = request.POST.getlist('certificate_name[]')
        institutions = request.POST.getlist('institution_name[]')
        years = request.POST.getlist('year_of_completion[]')
        files = request.FILES.getlist('certificate[]')


        certificates = []
        for i in range(len(types)):
            certificates.append({
                'certificate_type': types[i],
                'certificate_name': names[i],
                'institution_name': institutions[i],
                'year_of_completion': years[i],
                'certificate': fs.save(files[i].name, files[i]) if files[i] else None,
            })

        request.session['certificates'] = certificates

        with transaction.atomic():
            gi_data = request.session['general_info']
            program = Programs.objects.get(id=gi_data['program_id'])
            general = General_Information.objects.create(
                **{k: v for k, v in gi_data.items() if k not in ['NRC_scan', 'deposit_slip', 'passport_photo', 'program_id']},
                NRC_scan=gi_data['NRC_scan'],
                deposit_slip=gi_data['deposit_slip'],
                passport_photo=gi_data['passport_photo'],
                program=program,
            )

            Next_of_Kin.objects.create(
                addmission_id=general,
                **request.session['next_of_kin']
            )

            for r in request.session['results']:
                CertificateResults.objects.create(
                    admission_id=general,
                    **r
                )

            for cert in request.session['certificates']:
                School_Certificate.objects.create(
                    addmission=general,
                    certificate_type=cert['certificate_type'],
                    certificate_name=cert['certificate_name'],
                    institution_name=cert['institution_name'],
                    year_of_completion=cert['year_of_completion'],
                    certificate=cert['certificate'],
                )

        request.session.flush()
        return redirect('Application:success')

    return render(request, 'applications/step4_certificate.html', {'progress': 100})

def success(request):
    return render(request, 'Applications/success.html')

@login_required(login_url='/auth/login')
def accept(request, pk):
    user_id=request.user.id
    accepted_by=CustomUser.objects.get(id=user_id)
    if request.user.role == 'ADMIN':
        admission_id = General_Information.objects.get(pk=pk)
        app_status = Application_Status.objects.get(application=admission_id)
        app_status.status='APPROVED'
        app_status.accepted_by= accepted_by
        app_status.save()
        messages.success(request, "Applicant accepted Successfully")


        #Send acceptance email to applicant
        student_id = Student.objects.get(NRC=admission_id.NRC).id
        default_password =  'Pass123'  # Default password
        subject = 'Application Accepted'
        message = f'Dear {admission_id.first_name} {admission_id.last_name},\n\nCongratulations! Your application for the {admission_id.program} programme has been accepted.\n\n Your id is {student_id} \n\n Your Password: {default_password} \n\nBest regards,\nIdeal College Admissions Team'
        recipient_list = [admission_id.email]
        from_email = settings.EMAIL_HOST_USER
        
        email_message = EmailMessage(subject, message, from_email, recipient_list)
        
        EmailThread(email_message).start()
        return redirect('Application:recent')
    else:
        messages.error(request, 'Insufficient Privelleges')
    return redirect("Application:recent")

# --------------Recent Applications
@login_required(login_url='/auth/login')
def recent_applications(request):
    if request.user.role == 'ADMIN':
        applications =General_Information.objects.all().order_by('-date_of_application')

        context={
            'applications':applications,
        }
    else:
        return HttpResponse("<h1>Insufficent Roles</h1>")
    return render(request, 'applications/recent-applications.html', context)

def accepted_students(request):
    applications =General_Information.objects.all().order_by('-date_of_application')

    context = {
        'applications':applications
    }
    return render(request, 'applications/accepted_students.html', context)

#----------View Application Details----------------
@login_required(login_url='/auth/login')
def view_application(request, admission_id):
    if request.user.role == 'ADMIN':
        application = General_Information.objects.get(admission_id=admission_id)
        results = CertificateResults.objects.filter(admission_id=application)
        school_certificates = School_Certificate.objects.filter(addmission=application)
        if Application_Status.objects.filter(application=application).exists():
            application_status = Application_Status.objects.get(application=application)
            if Next_of_Kin.objects.filter(addmission_id=application).exists():
                next_of_kin = Next_of_Kin.objects.get(addmission_id=application)
            else:
                next_of_kin = None
            context={
                'application':application,
                'results':results,
                'school_certificates':school_certificates,
                'next_of_kin':next_of_kin,
                'application_status':application_status,
            }
        else:
            messages.error(request, 'Insufficient Privelleges')
    return render(request, 'applications/view_application.html', context)

#-----delete certificate file, passport photo, deposit slip when application is deleted
def delete_files(application):
    # Delete deposit slip
    if application.deposit_slip and os.path.isfile(application.deposit_slip.path):
        os.remove(application.deposit_slip.path)
    # Delete passport photo
    if application.passport_photo and os.path.isfile(application.passport_photo.path):
        os.remove(application.passport_photo.path)
    # Delete school certificates
    school_certificates = School_Certificate.objects.filter(addmission=application)
    for cert in school_certificates:
        if cert.certificate and os.path.isfile(cert.certificate.path):
            os.remove(cert.certificate.path)
#def reject application
@login_required(login_url='/auth/login')
def reject(request, pk):
    admission_id = General_Information.objects.get(pk=pk)
    app_status = Application_Status.objects.get(application=admission_id)
    app_status.status='REJECTED'
    app_status.save()

    messages.success(request, "Applicant rejected Successfully")
    return redirect("Application:recent")

#---- delete application if status is rejected
@login_required(login_url='/auth/login')
def delete_application(request, pk):
    admission_id = General_Information.objects.get(pk=pk)
    app_status = Application_Status.objects.get(application=admission_id)
    if app_status.status == 'REJECTED':
        admission_id.delete()
        messages.success(request, "Application deleted successfully.")
    else:
        messages.error(request, "Only rejected applications can be deleted.")
    return redirect("Application:recent")

