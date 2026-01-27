from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Courses.models import *
from Academics.models import *
from Users.models import CustomUser

# Create your views here.
@login_required(login_url='/auth/login')
def dashboard(request):
    if request.user.role == 'ADMIN':
        years = YearOfStudy.objects.all()
        session_years = SessionYear.objects.all()

        #count some data
        student_count = CustomUser.objects.filter(role='STUDENT').count()
        staff_count = CustomUser.objects.filter(role='STAFF').count()
        course_count = Courses.objects.all().count
        program_count = Programs.objects.all().count()

        context = {
            'years':years,
            'session_years':session_years,
            'student_count':student_count,
            'staff_count':staff_count,
            'course_count':course_count,
            'program_count':program_count,
            }
    else:
        pass
    return render(request, 'admin/dashboard.html', context)

def years_of_study(request):
    years = YearOfStudy.objects.all()
    return render(request, 'admin/dashboard.html', {'years':years})