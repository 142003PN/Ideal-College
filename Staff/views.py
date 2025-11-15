from django.shortcuts import render
from .models import Staff, StaffProfile
from .forms import StaffForm, ProfileForm
from django.contrib import messages
from django.http import *
from django.contrib.auth.decorators import login_required

#------------Staff List-----------------
@login_required(login_url='/users/login/')
def staff_list(request):
    staffs=Staff.objects.filter(role="STAFF")
    profile = StaffProfile.objects.all()

    context={'staffs':staffs, 'profile':profile}
    return render(request, 'staff/staff-list.html', context)
#---------------add staff member-------------------------
@login_required(login_url='/users/login/')
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            staff=form.save(commit=False)
            staff.role='STAFF'
            password = form.cleaned_data.get('password')
            staff.set_password(password)
            staff.save()
            if StaffProfile.objects.filter(staff_id=staff).exists():
                messages.error(request, 'Staff Already exists')
            else:
                profile = profile_form.save(commit=False)
                profile.staff_id = staff
                profile_form.save()
                messages.success(request, 'Staff added successfully.')
                return redirect('staff_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StaffForm()
        profile_form = ProfileForm()
    context = {
        'form':form,
        'profile_form':profile_form
    }
    return render(request, 'staff/add-staff.html', context)

#------------Edit Staff ----------------
@login_required(login_url='/users/login/')
def edit_staff(request, pk):
    staff_id=Staff.objects.get(pk=pk)
    profile=StaffProfile.objects.get(staff_id=staff_id)

    title = 'Edit Staff'

    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff_id)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid() and profile_form.is_valid():
            form.save(commit=False)
            profile_form.save(commit=False)
            
            messages.success(request, 'Staff updated successfully.')
        else:
            return HttpResponse("Form is not valid")
            
    else:
        form = StaffForm(instance=staff_id)
        profile_form = ProfileForm(instance=profile)
    context ={
        'form':form,
        'profile_form':profile_form,
        'title':title
    }
    return render(request, 'staff/add-staff.html', context)