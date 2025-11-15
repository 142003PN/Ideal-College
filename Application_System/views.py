from django.shortcuts import render, redirect
from Programs.models import Programs
from Students.models import Student, StudentProfile
from .models import *
from Courses.models import YearOfStudy
from django.contrib import messages
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

# Create your views here.
def apply(request):
    programs = Programs.objects.all()
    year = YearOfStudy.objects.get(year_title="First Year")
    data = request.session.get('form_data', {})
    if request.method == 'POST':
        #retrieve general information
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        nationality = request.POST.get('nationality')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        NRC = request.POST.get('NRC')
        marital_status = request.POST.get('marital_status')
        disability=request.POST.get('disability')
        disability_desc=request.POST.get('disability_desc')
        city_of_residence = request.POST.get('city_of_residence')
        program_id = request.POST.get('program')
        year_id = request.POST.get('year_of_study')
        year_of_study = YearOfStudy.objects.get(id=year_id)
        program = Programs.objects.get(id=program_id)
        deposit_slip = request.FILES.get('deposit_slip')
        passport_photo = request.FILES.get('passport_photo')
        #Subjects
        subjects = request.POST.getlist('subject')
        grades = request.POST.getlist('grade')
        #school certificate info
        certificate_types = request.POST.getlist('certificate_type')
        institution_names = request.POST.getlist('institution_name')
        completion_years = request.POST.getlist('completion_year')
        certificates = request.FILES.getlist('certificate')
        #Next of kin info
        full_name= request.POST.get('full_name')
        NK_email= request.POST.get('NK_email')
        phone_no = request.POST.get('phone_no')
        #validation
        if Student.objects.filter(email=email).exists() or General_Information.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
        elif Student.objects.filter(NRC=NRC).exists() or General_Information.objects.filter(NRC=NRC).exists():
            messages.error(request, 'NRC already exists!')
        elif len(NRC) > 15:
            messages.error(request, "NRC should have less than 15 characters")
        elif not all(c.isdigit() or c == '/' for c in NRC):
            messages.error(request, "NRC should only contain numbers and forward slashes /")
        # ensure all uploaded certificates are PDFs
        elif any(cert and not (getattr(cert, 'content_type', '') == 'application/pdf' or cert.name.lower().endswith('.pdf')) for cert in certificates):
            messages.error(request, 'All uploaded certificates must be PDF files.')
        else:
            #save general info
            addmission = General_Information.objects.create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                gender=gender,
                disability=disability,
                disability_desc=disability_desc,
                nationality=nationality,
                address=address,
                phone_number=phone_number,
                email=email,
                NRC=NRC,
                marital_status=marital_status,
                city_of_residence=city_of_residence,
                program=program,
                year_of_study=year_of_study,
                deposit_slip=deposit_slip,
                passport_photo=passport_photo
            )
            request.session['form_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'nationality': nationality,
                'address': address,
                'phone_number': phone_number,
                'email': email,
                'NRC': NRC,
                'marital_status': marital_status,
                'disability': disability,
                'disability_desc': disability_desc,
                'city_of_residence': city_of_residence,
                'program_id': program_id,
                'year_id': year_id,
                'subjects': subjects,
                'grades': grades,
                'certificate_types': certificate_types,
                'institution_names': institution_names,
                'completion_years': completion_years,
                'full_name': full_name,
                'NK_email': NK_email,
                'phone_no': phone_no,
            }
            #save certificate results
            for subject, grade in zip(subjects, grades):
                subject = CertificateResults.objects.create(
                    admission_id = addmission,
                    subject_name=subject,
                    grade = grade
                )
            #save school certificate info
            for cert_type, institution_name, completion_year, certificate in zip(certificate_types, institution_names, completion_years, certificates):
                school_cert = School_Certificate.objects.create(
                    addmission=addmission,
                    certificate_type=cert_type,
                    institution_name=institution_name,
                    year_of_completion=completion_year,
                    certificate=certificate
                )
            #save next of kin info
            next_of_kin = Next_of_Kin.objects.create(
                addmission_id=addmission,
                full_name=full_name,
                email=NK_email,
                phone_number=phone_no,
            )
            addmission.save();
            subject.save();
            school_cert.save();
            next_of_kin.save();
            # Clear session data after submission
            del request.session['form_data']
            messages.success(request, 'Application Submmited Successfully!')
    return render(request, 'applications/apply.html', {'programs': programs, 'year': year, 'data': data})

@login_required(login_url='/users/login/')
def accept(request, pk):
    admission_id = General_Information.objects.get(pk=pk)
    app_status = Application_Status.objects.get(application=admission_id)
    app_status.status='APPROVED'
    app_status.save()

    messages.success(request, "Applicant accepted Successfully")
    return redirect("Application:recent")

# --------------Recent Applications
@login_required(login_url='/users/login/')
def recent_applications(request):
    applications =General_Information.objects.all().order_by('-date_of_application')
    applications =General_Information.objects.all().order_by('-date_of_application')

    context={
        'applications':applications
    }
    return render(request, 'applications/recent-applications.html', context)

#----------View Application Details----------------
@login_required(login_url='/users/login/')
def view_application(request, admission_id):
    application = General_Information.objects.get(admission_id=admission_id)
    results = CertificateResults.objects.filter(admission_id=application)
    school_certificates = School_Certificate.objects.filter(addmission=application)
    if Application_Status.objects.get(application=application):
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
    return render(request, 'applications/view_application.html', context)
