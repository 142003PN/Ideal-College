from django.shortcuts import render, redirect
from .models import Student, StudentProfile
from .forms import StudentForm, StudentProfileForm
from django.contrib import messages
from django.http import *
import os
# Create your views here.

#list students view
def list_students(request):
    students = Student.objects.filter(role="STUDENT")
    profile = StudentProfile.objects.all()
    context = {
        'students': students,
        'profile': profile,
    }
    return render(request, 'Students/students.html', context)
#add student view
def add_student(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        profile_form = StudentProfileForm(request.POST, request.FILES)
        if student_form.is_valid() and profile_form.is_valid():
            student = student_form.save(commit=False)
            student.role = 'STUDENT'
            password = student_form.cleaned_data.get('password')
            student.set_password(password)
            student.save()
            if StudentProfile.objects.filter(student_id=student).exists():
                messages.error(request, "Student profile already exists.")
            else:
                profile = profile_form.save(commit=False)
                profile.student_id = student
                profile_form.save()
                messages.success(request, 'Student added successfully.')
                return redirect('Students:list')
        else:
            messages.error(request, 'Failed')
    else:
        student_form = StudentForm()
        profile_form = StudentProfileForm()
    
    context = {
        'student_form': student_form,
        'profile_form': profile_form,
    }
    return render(request, 'Students/add-student.html', context)

#edit student view
def edit_student(request, pk):
    studentt = Student.objects.get(pk=pk)
    profiles = StudentProfile.objects.get(student_id=studentt)
    if request.method == 'POST':
       student_form = StudentForm(request.POST, instance=studentt)
       profile_form = StudentProfileForm(request.POST, request.FILES, instance=profiles)
       if student_form.is_valid() and profile_form.is_valid():
           student = student_form.save(commit=False)
    else:
        student_form = StudentForm(instance=studentt)
        profile_form = StudentProfileForm(instance=profiles)
    context = {
        'student_form': student_form,
        'profile_form': profile_form,
    }
    return render(request, 'Students/add-student.html', context)

#student details view
def student_details(request, student_id):
    student = Student.objects.get(id=student_id)
    profile = student.profile
    context = {
        'student': student,
        'profile': profile,
    }
    return render(request, 'Students/student-details.html', context)

#delete student
def delete_student_media(student):
    try:
        profile = StudentProfile.objects.get(student_id=student)
        if profile.profile_picture and hasattr(profile.profile_picture, 'path'):
            if os.path.isfile(profile.profile_picture.path):
                os.remove(profile.profile_picture.path)
    except:
        pass

def delete_student(request, pk):
    try:
        student = Student.objects.get(pk=pk)
        delete_student_media(student)
        student.delete()
        return redirect('Students:list')
    except student.DoesNotExist:
        return HttpResponse("Student does not exixt")