from django.shortcuts import render
from .models import Registration
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
from Students.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Academics.models import SessionYear
# Create your views here.

#----------Register for Courses-------------
@login_required(login_url='/users/login/')
def register(request):
    #Get the logged in user
    sid = request.user
    #get program for the logged in user
    program=request.user.profile.program
    #get program for the logged in user
    student = StudentProfile.objects.get(student_id=sid)
    #get courses related to the logged in users programme of study
    years = YearOfStudy.objects.filter()
    courses = Courses.objects.filter(program_id=program)
    session_year=SessionYear.objects.get(is_current_year=1)
    if request.method =='POST':
        student_id=request.user
        year_of_study_id=request.POST.get('year_of_study')
        year_of_study=YearOfStudy.objects.get(id=year_of_study_id)
        selected_courses=request.POST.getlist('courses')

        
        reg=Registration.objects.create(
            student_id=student_id,
            year_of_study=year_of_study,
            session_year=session_year,
        )
        reg.courses.set(selected_courses)
        reg.save();
        messages.success(request, "Successfully submited awaiting Approval")

    context={
        'courses':courses,
        'years':years,
        'student':student,
        'program':program,
    }
    return render(request, 'registration/register.html', context)

def recent_registrations(request):
    registrations = Registration.objects.all()
    return render(request, 'registration/recently_registered.html', {'registrations': registrations})