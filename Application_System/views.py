from django.shortcuts import render
from Programs.models import Programs
from Students.models import Student, StudentProfile
from .models import *
from Courses.models import YearOfStudy
from django.contrib import messages
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
        certificate_type = request.POST.get('certificate_type')
        institution_name = request.POST.get('institution_name')
        completion_year = request.POST.get('completion_year')
        certificate = request.FILES.get('certificate')
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
            school_cert = School_Certificate.objects.create(
                addmission=addmission,
                certificate_type=certificate_type,
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