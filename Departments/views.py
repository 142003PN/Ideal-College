from django.shortcuts import render
from .models import Department
from .forms import DepartmentForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# ---------List departments------------
@login_required(login_url='/users/login/')
def departments(request):
    departments = Department.objects.all().order_by('-date_added')
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
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.info(request, "Department updated")
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'departments/edit-department.html', {'form':form})

#-----------delete department-----------------
@login_required(login_url='/users/login/')
def delete_department(request, pk):
    department = Department.objects.get(id=pk)
    department.delete()
    messages.info(request, "Department deleted")
    return render(request, 'departments/departments.html', {'departments':department})
