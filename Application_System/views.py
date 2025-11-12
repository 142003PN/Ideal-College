from django.shortcuts import render, redirect
from Programs.models import Programs
from Students.models import Student, StudentProfile
from .models import *
from Courses.models import YearOfStudy
from django.contrib import messages
import os
# Create your views here.
def apply(request):
    programs = Programs.objects.all()
    year = YearOfStudy.objects.get(year_title="First Year")

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
            return render(request, 'applications/apply.html', {'programs': programs})
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
            messages.success(request, 'Application Submmited Successfully!')
    return render(request, 'applications/apply.html', {'programs': programs, 'year': year})

def recent_applications(request):
    applications =General_Information.objects.all().order_by('-date_of_application')
    applications =General_Information.objects.all().order_by('-date_of_application')

    context={
        'applications':applications
    }
    return render(request, 'applications/recent-applications.html', context)
#----------View Application Details----------------
def view_application(request, admission_id):
    application = General_Information.objects.get(admission_id=admission_id)
    results = CertificateResults.objects.filter(admission_id=application)
    school_certificates = School_Certificate.objects.filter(addmission=application)
    next_of_kin = Next_of_Kin.objects.get(addmission_id=application)

    context={
        'application':application,
        'results':results,
        'school_certificates':school_certificates,
        'next_of_kin':next_of_kin
    }
    return render(request, 'applications/view_application.html', context)

def general_info(request):
    programs = Programs.objects.all()
    data = request.session.get('form_data', {})  # Ensure data is available for both GET and POST

    current_step = 1
    progress = 25
    if request.method == 'POST':
        if 'next' in request.POST:
            # Retrieve general information
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            date_of_birth = request.POST.get('date_of_birth')
            gender = request.POST.get('gender')
            NRC = request.POST.get('NRC')
            marital_status = request.POST.get('marital_status')
            disability = request.POST.get('disability')
            disability_desc = request.POST.get('disability_desc')
            deposit_slip = request.FILES.get('deposit_slip')
            passport_photo = request.FILES.get('passport_photo')

            # You can't store file objects in session — consider saving them or using temporary storage
            request.session['form_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'NRC': NRC,
                'marital_status': marital_status,
                'disability': disability,
                'disability_desc': disability_desc,
                # Store filenames or use other strategies for file handling
                'deposit_slip': deposit_slip.name if deposit_slip else '',
                'passport_photo': passport_photo.name if passport_photo else '',
            }

            # You may want to save files to a temporary model or storage here

            return redirect('Application:step2')

    return render(request, 'apply/general_info.html', {
        'data': data,
        'programs': programs,
        'current_step': current_step,
        'progress': 25,
        'progress': progress
    })

def step2(request):
    progress = 50
    data = request.session.get('form_data', {})
    current_step = 2
    if not data:
        return redirect('Application:step1')
    #Contact info
    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('Application:step1')
        elif 'next' in request.POST:
            data['nationality']= request.POST.get('nationality')
            data['address']= request.POST.get('address')
            data['phone_number']= request.POST.get('phone_number')
            data['email'] = request.POST.get('email')
            data['city_of_residence'] = request.POST.get('city_of_residence')
            request.session['form_data'] = data

            return redirect('Application:step3')
    context={'data':data, 'progress':50, 'current_step': current_step, 'progress': progress}
    return render(request, 'apply/step2.html', context)

def step3(request):
    current_step = 3
    progress = 75
    year = YearOfStudy.objects.get(year_title="First Year")
    programs = Programs.objects.all()
    data = request.session.get('form_data', {})
    if not data:
        return redirect('Application:step1')
    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('Application:step2')
        elif 'next' in request.POST:
            program_id = request.POST.get('program')
            year_id = request.POST.get('year_of_study')
            
            data['program'] = program_id
            data['year_of_study'] = year_id
            request.session['form_data'] = data
            return redirect('Application:step4')
    context={
        'programs':programs,
        'year':year,
        'data': data, 
        'progress': 75,
        'current_step': current_step,
        'progress': progress,
    }
    return render(request, 'apply/step3.html', context)

def step4(request):
    data = request.session.get('form_data')
    if not data:
        return redirect('Application:step1')

    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('Application:step3')
        elif 'submit' in request.POST:
            admission = General_Information.objects.create(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                date_of_birth=data.get('date_of_birth'),
                gender=data.get('gender'),
                NRC=data.get('NRC'),
                marital_status=data.get('marital_status'),
                disability=data.get('disability'),
                disability_desc=data.get('disability_desc'),
                #contact details
                email=data.get('email'),
                phone_number=data.get('phone_number'),
                address=data.get('address'),
                city_of_residence=data.get('city_of_residence'),
                nationality=data.get('nationality'),
                #program and year   
                program=Programs.objects.get(id=data.get('program')),
                year_of_study=YearOfStudy.objects.get(id=data.get('year_of_study')),
                #files would need to be handled properly
                deposit_slip=data.get('deposit_slip'),
                passport_photo=data.get('passport_photo')
            )
            admission.save();
            # Clear session data after submission
            del request.session['form_data']
            messages.success(request, 'Application Submitted Successfully!')
            return redirect('Application:step1')

    return render(request, 'apply/step4.html', {'data': data, 'progress': 100})

#---------------Delete Application-----------------
def delete_application_media(application):
    if application.deposit_slip:
        if os.path.isfile(application.deposit_slip.path):
            os.remove(application.deposit_slip.path)
    # Delete certificate
    try:
        school_cert = School_Certificate.objects.get(addmission=application)
        if school_cert.certificate:
            if os.path.isfile(school_cert.certificate.path):
                os.remove(school_cert.certificate.path)
    except School_Certificate.DoesNotExist:
        pass
        if os.path.isfile(application.certificate.path):
            os.remove(application.certificate.path)
    # Delete passport photo
    if application.passport_photo:
        if os.path.isfile(application.passport_photo.path):
            os.remove(application.passport_photo.path)
def delete_application(request, admission_id):
    application = General_Information.objects.get(admission_id=admission_id)
    delete_application_media(application)
    application.delete()
    messages.success(request, 'Application Deleted Successfully!')
    return redirect('Application:recent_applications')