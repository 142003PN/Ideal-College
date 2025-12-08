from django.shortcuts import render, redirect
from .models import Department
from .forms import DepartmentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from Staff.models import *
from Courses.models import Courses
from Programs.models import Programs
# ---------List departments------------
@login_required(login_url='/users/login/')
def departments(request):
    if request.user.role=='ADMIN':
        departments = Department.objects.all().order_by('-date_added')
    else:
        return HttpResponse('<h1>You can not View Departments</h1>')
    return render(request, 'departments/departments.html', {'departments':departments})
#-------------add department------------
@login_required(login_url='/users/login/')
def add_department(request):
    if request.user.role=='ADMIN':
        if request.method == 'POST':
            form = DepartmentForm(request.POST)
            user=request.user.id
            department_name=request.POST.get('department_name')
            if Department.objects.filter(department_name=department_name).exists():
                messages.error(request, "Department with this name already exists.")
                return redirect('Departments:add')
            added_by=CustomUser.objects.get(id=user)
            if form.is_valid():
                newdept = form.save(commit=False)
                newdept.added_by=added_by
                form.save()
                messages.info(request, "Department added")
        else:
            form = DepartmentForm()
    else:
        HttpResponse('<h1>Insufficient Privelleges</h1>')
    return render(request, 'departments/add-department.html', {'form':form})

#-----------edit department-------------
@login_required(login_url='/users/login/')
def edit_department(request, pk):
    if request.user.role=='ADMIN':
        department = Department.objects.get(id=pk)
        if request.user.role=='ADMIN':
            if request.method == 'POST':
                form = DepartmentForm(request.POST, instance=department)
                if form.is_valid():
                    form.save()
                    messages.info(request, "Department updated")
            else:
                form = DepartmentForm(instance=department)
        else:
            return HttpResponse('<h1>You cant view Departments')
    else:
        HttpResponse('<h1>Insufficient Privelleges</h1>')
    return render(request, 'departments/edit-department.html', {'form':form})

#-----------delete department-----------------
@login_required(login_url='/users/login/')
def delete_department(request, pk):
    if request.user.role=='ADMIN':
        department = Department.objects.get(id=pk)
        department.delete()
        messages.info(request, "Department deleted")
    else:
        HttpResponse('<h1>Insufficient Privelleges</h1>')
    return render(request, 'departments/departments.html', {'departments':department})

#------------Department Dashboard-----------
def dashboard(request):
    if request.user.staff_profile.position =='HOD':
        department = request.user.staff_profile.department
        programs = Programs.objects.filter(department_id=department)
        staff_members = StaffProfile.objects.filter(department=department)

        #-------Count Some data related to the department
        staff_count = StaffProfile.objects.filter(department=department).count()
        program_count = Programs.objects.filter(department_id=department).count()

        context={
            'department':department,
            'programs':programs,
            'staff_members':staff_members,
            'staff_count': staff_count,
            'program_count': program_count,
        }
    else:
        HttpResponse('<h1>Insufficient Roles<h1/>')
    return render(request, 'departments/dashboard.html', context)