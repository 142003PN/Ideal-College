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
        city_of_residence = request.POST.get('city_of_residence')
        program_id = request.POST.get('program')
        year_id = request.POST.get('year_of_study')
        year_of_study = YearOfStudy.objects.get(id=year_id)
        program = Programs.objects.get(id=program_id)
        deposit_slip = request.FILES.get('deposit_slip')
        passport_photo = request.FILES.get('passport_photo')
        #school certificate info
        certificate_type = request.POST.get('certificate_type')
        institution_name = request.POST.get('institution_name')
        completion_year = request.POST.get('completion_year')
        certificate = request.FILES.get('certificate')
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
            #save school certificate info
            school_cert = School_Certificate.objects.create(
                addmission=addmission,
                certificate_type=certificate_type,
                institution_name=institution_name,
                year_of_completion=completion_year,
                certificate=certificate
            )
            addmission.save();
            school_cert.save();
            messages.success(request, 'Application Submmited Successfully!')
    return render(request, 'applications/apply.html', {'programs': programs, 'year': year})