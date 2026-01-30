from django.shortcuts import get_object_or_404, render, redirect
from .models import Registration
from Academics.models import *
from Courses.models import Courses
from Students.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from Academics.models import SessionYear
import datetime
from django.template.loader import render_to_string
from django.http import *
from Fees.models import *
import tempfile
import os

"""
    1. Register for Courses
    2. View Recent Registrations
    3. Approve Course Registration
    4. View Submitted Courses
    5. Print Confirmation Slip
    6. Deregister Registration
"""

#1. ----------Register for Courses-------------
@login_required(login_url='/')
def register(request):
    sid = request.user
    program = request.user.profile.program
    student = StudentProfile.objects.get(student_id=sid)
    years = YearOfStudy.objects.all()
    courses = Courses.objects.filter(program_id=program)
    intake = request.user.profile.intake
    semesters = Semester.objects.all()

    # Check if session year exists for intake
    session_year_qs = SessionYear.objects.filter(intake=intake, is_current_year=True)
    no_session_year = not session_year_qs.exists()

    if no_session_year:
        session_year = None
        already_registered = False
    else:
        session_year = session_year_qs.first()
        already_registered = Registration.objects.filter(student_id=sid, session_year=session_year).exists()

        if already_registered and request.method == 'POST':
            messages.warning(request, "You have already registered for the current session year.")

        elif request.method == 'POST':
            semester = Semester.objects.get(id=request.POST.get('semester'))
            year_of_study = YearOfStudy.objects.get(id=request.POST.get('year_of_study'))
            selected_courses = request.POST.getlist('courses')

            if not year_of_study:
                messages.error(request, "Please select a year of study")
                return redirect('Registration:register')

            reg = Registration.objects.create(
                student_id=sid,
                year_of_study=year_of_study,
                session_year=session_year,
                semester=semester,
            )
            reg.courses.set(selected_courses)
            messages.success(request, "Successfully submitted awaiting Approval")
            return redirect('Registration:register')

    context = {
        'courses': courses,
        'years': years,
        'student': student,
        'program': program,
        'already_registered': already_registered,
        'semesters': semesters,
        'no_session_year': no_session_year
    }

    return render(request, 'registration/register.html', context)

#2. ----------------View Recent Registrations-----------------
@login_required(login_url='/')
def recent_registrations(request):
    registrations = Registration.objects.all().order_by('-registration_date')
    return render(request, 'registration/recently_registered.html', {'registrations': registrations})

#3. ------------------Approve Course Registration----------------------------
@login_required(login_url='/')
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
        except Registration.DoesNotExist:
            messages.error(request, "Registration not found.")
    return render(request, 'registration/recently_registered.html')

#4. --------------------View Submitted Courses-------------
@login_required(login_url='/')
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

#5. ----------------Print Confirmation Slip-----------------
@login_required(login_url='/')
def print_confirmation_slip(request, student_id):
    intake = StudentProfile.objects.get(student_id=student_id).intake

    session_year_qs = SessionYear.objects.filter(intake=intake, is_current_year=True)

    #Check if session year exists
    if not session_year_qs.exists():
        messages.error(request, "Current session year not set for your intake. Please contact administration.")

    session_year = session_year_qs.first()

    # Check if student is registered
    is_registered = Registration.objects.filter(student_id=student_id, session_year=session_year).exists()

    not_registered = not is_registered
    if not_registered:
        return render(request, 'registration/confirmation-slip.html', {'not_registered': not_registered})
    #get registration and courses
    if is_registered:
        registration = Registration.objects.get(student_id=student_id, session_year=session_year)
        courses = registration.courses.all()
        today = datetime.date.today()

        #add a student ledger to the financial slip
        account = get_object_or_404(StudentAccount, id=student_id)
        student_id = get_object_or_404(Student, id=student_id)

        entries = LedgerEntry.objects.filter(
            account=account
        ).order_by('created_at')

        running_balance = 0
        statement = []

        for entry in entries:
            if entry.entry_type == LedgerEntry.EntryType.DEBIT:
                running_balance += entry.amount
                debit = entry.amount
                credit = None
            else:
                running_balance -= entry.amount
                debit = None
                credit = entry.amount
            id = entry.id
            statement.append({
                'date': entry.created_at,
                'description': entry.description,
                'debit': debit,
                'credit': credit,
                'balance': running_balance,
                'id':id,
                'is_reversal': entry.is_reversal
            })
            

        context={'courses': courses, 'registration': registration,
                    'today': today, 'student_id': student_id,
                    'account': account,
                    'statement': statement,
                    'final_balance': running_balance,
                    'session_year_': session_year,
                    'not_registered': not_registered,
                    'is_registered': is_registered
                }
            
    return render(request, 'registration/confirmation-slip.html', context)

#6. ----------------Delete Registration-----------------
def delete_qrcode_media(registration):
    try:
        if registration.qr_code and hasattr(registration.qr_code, 'path'):
            if os.path.isfile(registration.qr_code.path):
                os.remove(registration.qr_code.path)
    except (AttributeError, OSError):
        pass
#7. ---------------------------Deregister--------------------------------
@login_required(login_url='/')
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
    