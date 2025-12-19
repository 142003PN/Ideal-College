from django.shortcuts import render, redirect
from .models import Registration
from Academics.models import SessionYear
from Courses.models import Courses, YearOfStudy
from Students.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Academics.models import SessionYear
import datetime
from django.template.loader import render_to_string
from django.http import *


import tempfile
import os

# Create your views here.


#----------Register for Courses-------------
@login_required(login_url='/users/login/')
def register(request):
    # Get the logged in user
    sid = request.user
    # get program for the logged in user
    program = request.user.profile.program
    # get student profile for the logged in user
    student = StudentProfile.objects.get(student_id=sid)
    # get courses related to the logged in user's programme of study
    years = YearOfStudy.objects.filter()
    courses = Courses.objects.filter(program_id=program)
    session_year = SessionYear.objects.get(is_current_year=1)

    # Prevent multiple registrations in the same session year
    already_registered = Registration.objects.filter(student_id=sid, session_year=session_year).exists()
    if already_registered and request.method == 'POST':
        messages.warning(request, "You have already registered for the current session year.")
    elif request.method == 'POST':
        year_of_study_id = request.POST.get('year_of_study')
        year_of_study = YearOfStudy.objects.get(id=year_of_study_id)
        selected_courses = request.POST.getlist('courses')

        if year_of_study is None:
            messages.error(request, "Please select a year of study")
            return redirect('Registration:register')
        else:
            reg = Registration.objects.create(
                student_id=sid,
                year_of_study=year_of_study,
                session_year=session_year,
            )
            reg.courses.set(selected_courses)
            reg.save()
            messages.success(request, "Successfully submitted awaiting Approval")
            already_registered = True
            return redirect('Registration:register')

    context = {
        'courses': courses,
        'years': years,
        'student': student,
        'program': program,
        'already_registered': already_registered,
    }
    return render(request, 'registration/register.html', context)
#----------------View Recent Registrations-----------------
def recent_registrations(request):
    registrations = Registration.objects.all().order_by('-registration_date')
    return render(request, 'registration/recently_registered.html', {'registrations': registrations})

#------------------Approve Course Registration----------------------------
def approve_registration(request, pk):
    if request.user.role != 'STAFF' and request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to approve registrations.")
        return redirect('Registration:recent_registrations')
    else:
        try:
            student = StudentProfile.objects.get(student_id=Registration.objects.get(id=pk).student_id)
            registration = Registration.objects.get(id=pk)
            registration.status = 'Approved'
            student.year_of_study = registration.year_of_study
            registration.save()
            student.save()
            messages.success(request, "Registration approved successfully.")
            return redirect('Registration:recent')
        except Registration.DoesNotExist:
            messages.error(request, "Registration not found.")
    return render(request, 'registration/recently_registered.html')

#--------------------View Submitted Courses-------------
def view_submitted_courses(request, pk):
    if request.user.role=='ADMIN':
        try:
            registration = Registration.objects.get(id=pk)
            courses = registration.courses.all()


            return render(request, 'registration/view-registered.html', {'courses': courses, 'registration': registration})
        except Registration.DoesNotExist:
            messages.error(request, "Registration not found.")
            return redirect('Registration:recent')
    return render(request, 'registration/view-registered.html')

def print_confirmation_slip(request, student_id):
        
        student_id = request.user
        return render(request, 'registration/confirmation-slip.html', {'student_id': student_id})
"""
        #convert confirmation slip to pdf
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition']='attachment: filename=Confirmation'+'.pdf'
        response['Content-Transfer-Encoding'] = 'binary'

        session_year = SessionYear.objects.get(is_current_year=1)
        student_id = request.user
        registration = Registration.objects.get(student_id=student_id, session_year=session_year)
        courses = registration.courses.all()
        today = datetime.date.today()

        context={'courses': courses, 'registration': registration,
                        'today': today, 'student_id': student_id}
        
        html_string = render_to_string('registration/confirmation-slip.html', context)
        html = HTML(string=html_string)

        result = html.write_pdf()

        with tempfile.NamedTemporaryFile(delete=True) as output:
            output.write(result)
            output.flush()

            output=open(output.name, 'rb')
            response.write(output.read())
        return response
"""
#----------------Delete Registration-----------------
def delete_qrcode_media(registration):
    try:
        if registration.qr_code and hasattr(registration.qr_code, 'path'):
            if os.path.isfile(registration.qr_code.path):
                os.remove(registration.qr_code.path)
    except (AttributeError, OSError):
        pass
#deregister
def delete_registration(request, pk):
    if request.user.role != 'ADMIN':
        messages.error(request, "You do not have permission to delete registrations.")
        return redirect('Registration:recent_registrations')
    
    try:
        registration = Registration.objects.get(id=pk)
        delete_qrcode_media(registration)
        registration.delete()
        messages.success(request, "Registration deleted successfully.")
        return redirect('Registration:recent')
    except Registration.DoesNotExist:
        messages.error(request, "Registration not found.")
        return redirect('Registration:recent_registrations')