from datetime import datetime
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
@login_required(login_url='/')
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
@login_required(login_url='/')
def add_student(request):
    programmes=Programs.objects.all()
    years = YearOfStudy.objects.all()
    intakes = Intake.objects.all()
    
    if request.method == 'POST':
        #Retrieve student data from form
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        NRC=request.POST.get('NRC')
        #profile data
        intake_id=request.POST.get('intake')
        intake = Intake.objects.get(id=intake_id).id
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

        #generate student id
        intake_obj = Intake.objects.filter(id=intake).first()
        intake_gn = intake_obj.intake_name if intake_obj else 'unknown'

        year = datetime.now().year

        if intake_gn.lower() == 'january':
            intake_code = '01'
        elif intake_gn.lower() == 'july':
            intake_code = '02'
        else:
            intake_code = '00'

        prefix = f"{year}{intake_code}01"

        last_student = Student.objects.filter(id__startswith=prefix).order_by('-id').first()

        if last_student:
            last_serial = int(str(last_student.id)[-2:])
            new_serial = last_serial + 1
        else:
            new_serial = 1

        serial = str(new_serial).zfill(2)
        student_id = f"{prefix}{serial}"


        if Student.objects.filter(email=email).exists():
            messages.error(request, "Student with this ID already exists.")
            return redirect('Students:add') 
        elif Student.objects.filter(NRC=NRC).exists():
            messages.error(request, "Student with this NRC already exists.")
            return redirect('Students:add')
        elif len(NRC) > 15:
            messages.error(request, "NRC should have less than 15 characters")
            return redirect('Students:add')
        elif not all(c.isdigit() or c == '/' for c in NRC):
            messages.error(request, "NRC should only contain numbers and forward slashes /")
            return redirect('Students:add')
        else:
             #save student
            try:
                student=Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    id=student_id,
                    email=email,
                    NRC=NRC,
                )
                student.set_password(password)
                student.save()
                #save profile
                profile=StudentProfile.objects.create(
                    intake_id=intake,
                    gender=gender,
                    date_of_birth=date_of_birth,
                    address=address,
                    program=program,
                    phone_number=phone_number,
                    profile_picture=profile_picture,
                    year_of_study=year_of_study,
                    student_id=student
                )
                profile.save()
            except Exception as e:
                if student:
                    student.delete()
                messages.error(request, f"Error saving student: {str(e)}")
                return redirect('Students:add')
            messages.success(request, "Student Added Successfully")
    else:
        pass
    context={
        'programmes':programmes,
        'years':years,
        'intakes':intakes,
    }
    return render(request, 'students/add-student.html', context)

#-------------edit student view----------------
@login_required(login_url='/')
def edit_student(request, pk):
    student = Student.objects.get(pk=pk)
    profile = StudentProfile.objects.get(student_id=student)
    if not profile.program:
        programs = Programs.objects.all()
    else:
        programs = Programs.objects.filter(id=profile.program.id) | Programs.objects.exclude(id=profile.program.id)
    if not profile.intake:
        intakes = Intake.objects.all()
    else:
        intakes = Intake.objects.filter(id=profile.intake.id) | Intake.objects.exclude(id=profile.intake.id)

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
        intake_id = request.POST.get('intake')
        program_id = request.POST.get('programme')
        if request.user.role == 'ADMIN':
            program = Programs.objects.get(id=program_id)
            intake_obj = Intake.objects.get(id=intake_id)

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
        if request.user.role == 'ADMIN':
            # Update profile
            profile.gender = gender
            profile.date_of_birth = date_of_birth
            profile.address = address
            profile.phone_number = phone_number
            profile.program = program
            profile.intake = intake_obj
            profile.save()
            
            messages.success(request, 'Student updated successfully')
            return redirect('Students:details', student_id=pk)
        else:
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
        'programs': programs,
        'intakes': intakes,
    }
    return render(request, 'students/edit-student.html', context)

#-------------student details view-----------------
@login_required(login_url='/')
def student_details(request, student_id):
    #-------Update Profile Picture-----------
    try:
        student = Student.objects.get(pk=student_id).id
        student_profile = StudentProfile.objects.filter(student_id=student)
        if student_profile.exists():
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                if student_profile.profile_picture and hasattr(student_profile.profile_picture, 'path'):
                    if os.path.isfile(student_profile.profile_picture.path):
                        os.remove(student_profile.profile_picture.path)
                student_profile.profile_picture = profile_picture
                student_profile.save()
                messages.success(request, 'Profile picture updated successfully.')
        else:
            return redirect('Students:add-profile', student_id=student )
    except StudentProfile.DoesNotExist:
        return redirect('error404')
    #------------End of profile pic update-------
    student = Student.objects.get(id=student_id)
    profile = student.profile
    context = {
        'student': student,
        'profile': profile,
    }
    return render(request, 'students/student-details.html', context)

@login_required(login_url='/')
def add_profile(request, student_id):
    student_obj = Student.objects.get(id=student_id)
    programmes=Programs.objects.all()
    years = YearOfStudy.objects.all()
    intakes = Intake.objects.all()

    #get form data
    gender = request.POST.get('gender')
    date_of_birth = request.POST.get('date_of_birth')
    address = request.POST.get('address')
    phone_number = request.POST.get('phone_number')
    intake_id = request.POST.get('intake')
    program_id = request.POST.get('programme')
    year_id = request.POST.get('year_of_study')
    
    if request.method == 'POST':
        if request.user.role == 'ADMIN':
            year_of_study = YearOfStudy.objects.get(id=year_id)
            program_obj = Programs.objects.get(id=program_id)
            intake_obj = Intake.objects.get(id=intake_id).id
            StudentProfile.objects.create(
                intake_id=intake_obj,
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                program=program_obj,
                phone_number=phone_number,
                student_id=student_obj,
                year_of_study=year_of_study
            )
            messages.success(request, 'Profile Added')
            return redirect('Students:details', student_id=student_id)          
        elif request.user.role == 'ADMIN' and StudentProfile.objects.filter(student_id=student_obj).exists():
            messages.error(request, 'Profile already exists for this student')
            return redirect('Students:details', student_id=student_id)
        elif request.user.role == 'STUDENT' and str(request.user.id) == str(student_id):
            year_of_study = YearOfStudy.objects.get(id=year_id)
            intake_obj = Intake.objects.get(id=intake_id).id
            StudentProfile.objects.create(
                gender=gender,
                date_of_birth=date_of_birth,
                address=address,
                phone_number=phone_number,
                student_id=student_obj,
                year_of_study=year_of_study,
                intake=intake_obj,
            )
            messages.success(request, 'Profile Added')
            return redirect('Students:details', student_id=student_id)
        else:
            messages.error(request, 'Insufficient Privelleges to add profile')
            return redirect('Students:details', student_id=student_id)
    context={
        'intakes':intakes,
        'programmes':programmes,
        'years':years,
        'student_id':student_id
    }
    return render(request, 'students/add-profile.html', context)


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
@login_required(login_url='/')
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
@login_required(login_url='/')
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
