from django.shortcuts import render, redirect
from .models import Department
from .forms import DepartmentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

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
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            newdept = form.save(commit=False)
            form.save()
            messages.info(request, "Department added")
    else:
        form = DepartmentForm()
    return render(request, 'departments/add-department.html', {'form':form})

#-----------edit department-------------
@login_required(login_url='/users/login/')
def edit_department(request, pk):
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
    return render(request, 'departments/edit-department.html', {'form':form})

#-----------delete department-----------------
@login_required(login_url='/users/login/')
def delete_department(request, pk):
    department = Department.objects.get(id=pk)
    department.delete()
    messages.info(request, "Department deleted")
    return render(request, 'departments/departments.html', {'departments':department})
