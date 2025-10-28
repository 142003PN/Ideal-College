from django.shortcuts import render
from .models import Student, StudentProfile
from .forms import StudentForm, StudentProfileForm
from django.contrib import messages
# Create your views here.

#list students view
def list_students(request):
    students = Student.objects.filter(role=Student.Roles.STUDENT)
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
                return render(request, 'Students/success.html')
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
def edit_student(request, student_id):
    student = Student.objects.get(id=student_id)
    profile = student.profile

    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if student_form.is_valid() and profile_form.is_valid():
            student_form.save(commit=False)
            profile_form.save(commit=False)
            messages.success(request, 'Student updated successfully.')
            return render(request, 'Students/success.html')
    else:
        student_form = StudentForm(instance=student)
        profile_form = StudentProfileForm(instance=profile)

    context = {
        'student_form': student_form,
        'profile_form': profile_form,
        'student': student,
    }
    return render(request, 'Students/edit-student.html', context)

#student details view
def student_details(request, student_id):
    student = Student.objects.get(id=student_id)
    profile = student.profile
    context = {
        'student': student,
        'profile': profile,
    }
    return render(request, 'Students/student-details.html', context)