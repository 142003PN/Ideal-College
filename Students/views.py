from django.shortcuts import render, redirect
from .models import *
from Registration.models import *
from Academics.models import YearOfStudy
from Programs.models import Programs
from django.contrib import messages
from django.http import *
from django.contrib.auth.decorators import login_required
import os

#---------List Students-----------
@login_required(login_url='/users/login/')
def list_students(request):
    if request.user.role == 'ADMIN':
        students = Student.objects.filter(role="STUDENT").order_by('date_joined')
        profile = StudentProfile.objects.all()
    else:
        return HttpResponse("<h1>Insufficient Privelledges")
    context = {
            'students': students,
            'profile': profile,
        }
    return render(request, 'students/students.html', context)

#A----------Add student view---------------
@login_required(login_url='/users/login/')
def add_student(request):
    programmes=Programs.objects.all()
    years = YearOfStudy.objects.all()
    if request.method == 'POST':
        #Retrieve student data from form
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        student_id=request.POST.get('student_id')
        email=request.POST.get('email')
        NRC=request.POST.get('NRC')
        #profile data
        gender=request.POST.get('gender')
        date_of_birth=request.POST.get('date_of_birth')
        program_id=request.POST.get('programme')
        program = Programs.objects.get(id=program_id)
        address=request.POST.get('address')
        phone_number=request.POST.get('phone_number')
        profile_picture=request.FILES.get('profile_picture')
        year_id=request.POST.get('year_of_study')
        year_of_study = YearOfStudy.objects.get(id=year_id)
        password="Pass123"
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Student with this ID already exists.")
            return redirect('Students:add') 
        elif Student.objects.filter(NRC=NRC).exists():
            messages.error(request, "Student with this NRC already exists.")
            return redirect('Students:add')
        elif Student.objects.filter(id=student_id).exists():
            messages.error(request, "Student with this ID already exists.")
            return redirect('Students:add')
        elif len(NRC) > 15:
            messages.error(request, "NRC should have less than 15 characters")
            return redirect('Students:add')
        elif not all(c.isdigit() or c == '/' for c in NRC):
            messages.error(request, "NRC should only contain numbers and forward slashes /")
            return redirect('Students:add')
        else:
             #save student
            student=Student.objects.create(
                first_name=first_name,
                last_name=last_name,
                id=student_id,
                email=email,
                NRC=NRC,
            )
            student.set_password(password)
            student.save();
            #save profile
            profile=StudentProfile.objects.create(
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                program=program,
                phone_number=phone_number,
                profile_picture=profile_picture,
                year_of_study=year_of_study,
                student_id=student
            )
            profile.save();
            messages.success(request, "Student Added Successfully")
    else:
        pass
    context={
        'programmes':programmes,
        'years':years,
    }
    return render(request, 'students/add-student.html', context)

#-------------edit student view-------------------
@login_required(login_url='/users/login/')
def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    profile = StudentProfile.objects.get(student_id=student)
    
    if request.method == 'POST':
        # Retrieve student data from form  
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        NRC = request.POST.get('NRC')
        
        # Retrieve profile data
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')

        if email != student.email and Student.objects.filter(email=email).exists():
            messages.error(request, "Student with this email already exists.")
            return redirect('Students:edit', pk=pk)
        elif len(NRC) > 15:
            messages.error(request, "NRC should have less than 15 characters")
            return redirect('Students:edit', pk=pk)
        elif not all(c.isdigit() or c == '/' for c in NRC):
            messages.error(request, "NRC should only contain numbers and forward slashes /")
            return redirect('Students:edit', pk=pk)
        
        # Update student
        student.first_name = first_name
        student.last_name = last_name
        student.email = email
        student.NRC = NRC
        student.save()
        
        # Update profile
        profile.gender = gender
        profile.date_of_birth = date_of_birth
        profile.address = address
        profile.phone_number = phone_number
        profile.save()
        
        messages.success(request, 'Student updated successfully')
        return redirect('Students:details', student_id=pk)

    context = {
        'student': student,
        'profile': profile,
    }
    return render(request, 'students/edit-student.html', context)

#-------------student details view-----------------
@login_required(login_url='/users/login/')
def student_details(request, student_id):
    #-------Update Profile Picture-----------
    try:
        student = Student.objects.get(pk=student_id)
        student_profile = StudentProfile.objects.get(student_id=student)
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            if student_profile.profile_picture and hasattr(student_profile.profile_picture, 'path'):
                if os.path.isfile(student_profile.profile_picture.path):
                    os.remove(student_profile.profile_picture.path)
            student_profile.profile_picture = profile_picture
            student_profile.save()
            messages.success(request, 'Profile picture updated successfully.')
    except StudentProfile.DoesNotExist:
        pass
    #------------End of profile pic update-------
    student = Student.objects.get(id=student_id)
    profile = student.profile
    context = {
        'student': student,
        'profile': profile,
    }
    return render(request, 'students/student-details.html', context)

#----------delete student media----------------
def delete_student_media(student):
    try:
        profile = StudentProfile.objects.get(student_id=student)
        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
            if os.path.isfile(profile.profile_picture.path):
                os.remove(profile.profile_picture.path)
    except:
        pass
#----------Delete Student------------
@login_required(login_url='/users/login/')
def delete_student(request, pk):
    if request.user.role == 'ADMIN':
        try:
            student = Student.objects.get(pk=pk)
            delete_student_media(student)
            student.delete()
            return redirect('Students:list')
        except student.DoesNotExist:
            return HttpResponse("Student does not exixt")
    else:
        return HttpResponse("<h1>Insufficient Privelleges </h1>")
    
# Student dashboard view
@login_required(login_url='/users/login/')
def student_dashboard(request):
    student = request.user

    session_year = SessionYear.objects.filter(is_current_year=True).first()

    registration = None
    courses = []

    if session_year:
        registration = Registration.objects.filter(
            student_id=student,
            session_year=session_year
        ).first()
        if registration:
            courses = registration.courses.all()

    context = {
        'registration': registration,
        'courses': courses,
        'session_year': session_year,
    }
    return render(request, 'students/student-dashboard.html', context)
